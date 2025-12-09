#!/bin/bash
# MIA Enterprise AGI - Production Deployment Script
# Automated deployment with health checks and rollback capability

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="mia-enterprise-agi"
COMPOSE_FILE="docker-compose.enterprise.yml"
BACKUP_DIR="./backups"
LOG_FILE="./deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
        warning "Less than 10GB disk space available"
    fi
    
    success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./config"
    mkdir -p "./nginx"
    mkdir -p "./monitoring"
    mkdir -p "./sql"
    
    success "Directories created"
}

# Generate configuration files
generate_configs() {
    log "Generating configuration files..."
    
    # Nginx configuration
    cat > "./nginx/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream mia_backend {
        server mia-enterprise:12000;
    }
    
    server {
        listen 80;
        server_name _;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
        
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://mia_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /health {
            proxy_pass http://mia_backend/health;
            access_log off;
        }
    }
}
EOF
    
    # Prometheus configuration
    mkdir -p "./monitoring"
    cat > "./monitoring/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mia-enterprise'
    static_configs:
      - targets: ['mia-enterprise:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF
    
    success "Configuration files generated"
}

# Backup existing deployment
backup_deployment() {
    if [ -d "./mia_data" ]; then
        log "Creating backup of existing deployment..."
        
        backup_name="mia_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR/$backup_name"
        
        # Backup data
        cp -r ./mia_data "$BACKUP_DIR/$backup_name/" 2>/dev/null || true
        
        # Backup configuration
        cp -r ./config "$BACKUP_DIR/$backup_name/" 2>/dev/null || true
        
        success "Backup created: $backup_name"
    fi
}

# Build and deploy
deploy() {
    log "Starting deployment..."
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build MIA Enterprise image
    log "Building MIA Enterprise image..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache mia-enterprise
    
    # Start services
    log "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Deployment started"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Health check attempt $attempt/$max_attempts"
        
        if curl -f -s http://localhost:12000/health > /dev/null 2>&1; then
            success "Health check passed"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback function
rollback() {
    error "Deployment failed, initiating rollback..."
    
    # Stop current deployment
    docker-compose -f "$COMPOSE_FILE" down
    
    # Restore from backup if available
    latest_backup=$(ls -t "$BACKUP_DIR" | head -n1)
    if [ -n "$latest_backup" ]; then
        log "Restoring from backup: $latest_backup"
        cp -r "$BACKUP_DIR/$latest_backup/mia_data" ./ 2>/dev/null || true
        cp -r "$BACKUP_DIR/$latest_backup/config" ./ 2>/dev/null || true
    fi
    
    error "Rollback completed"
    exit 1
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    
    # Keep only last 5 backups
    cd "$BACKUP_DIR"
    ls -t | tail -n +6 | xargs -r rm -rf
    cd - > /dev/null
    
    success "Backup cleanup completed"
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    
    log "Service URLs:"
    echo "  Web Interface: http://localhost:12000"
    echo "  Core API: http://localhost:8000"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3000"
    echo ""
    
    log "Logs:"
    echo "  View logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  MIA logs: docker-compose -f $COMPOSE_FILE logs -f mia-enterprise"
}

# Main deployment function
main() {
    log "Starting MIA Enterprise AGI deployment..."
    
    # Trap errors for rollback
    trap rollback ERR
    
    check_prerequisites
    create_directories
    generate_configs
    backup_deployment
    deploy
    
    # Wait for services to start
    sleep 30
    
    if health_check; then
        cleanup_backups
        success "MIA Enterprise AGI deployed successfully!"
        show_status
    else
        rollback
    fi
}

# Command line options
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log "Stopping MIA Enterprise AGI..."
        docker-compose -f "$COMPOSE_FILE" down
        success "Services stopped"
        ;;
    "restart")
        log "Restarting MIA Enterprise AGI..."
        docker-compose -f "$COMPOSE_FILE" restart
        success "Services restarted"
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    "status")
        show_status
        ;;
    "update")
        log "Updating MIA Enterprise AGI..."
        docker-compose -f "$COMPOSE_FILE" pull
        docker-compose -f "$COMPOSE_FILE" up -d
        success "Update completed"
        ;;
    "backup")
        backup_deployment
        ;;
    "cleanup")
        log "Cleaning up Docker resources..."
        docker system prune -f
        docker volume prune -f
        success "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|update|backup|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy MIA Enterprise AGI"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - View service logs"
        echo "  status  - Show deployment status"
        echo "  update  - Update to latest version"
        echo "  backup  - Create backup"
        echo "  cleanup - Clean up Docker resources"
        exit 1
        ;;
esac