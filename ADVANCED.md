# Advanced Configuration Examples

This file contains advanced configuration examples for Headscale.

## Table of Contents

- [ACL Policies](#acl-policies)
- [Custom DNS Settings](#custom-dns-settings)
- [Exit Nodes](#exit-nodes)
- [Subnet Routing](#subnet-routing)
- [Firewall Configuration](#firewall-configuration)

---

## ACL Policies

ACL (Access Control Lists) allow you to control which devices can communicate with each other.

### Basic ACL Example

Create `/etc/headscale/acl.json`:

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["*"],
      "dst": ["*:*"]
    }
  ]
}
```

This allows all devices to communicate with each other (default behavior).

### Restricting Access Between Groups

```json
{
  "groups": {
    "group:admin": ["user1@example.com"],
    "group:servers": ["server1", "server2"],
    "group:clients": ["*"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["group:admin"],
      "dst": ["*:*"]
    },
    {
      "action": "accept",
      "src": ["group:clients"],
      "dst": ["group:servers:22,80,443"]
    }
  ]
}
```

This configuration:
- Admins can access everything
- Clients can only access servers on ports 22, 80, and 443

### Apply ACL Configuration

1. Edit Headscale config:
```bash
nano /etc/headscale/config.yaml
```

2. Set ACL path:
```yaml
policy:
  mode: file
  path: /etc/headscale/acl.json
```

3. Restart Headscale:
```bash
systemctl restart headscale
```

---

## Custom DNS Settings

### Override Local DNS

Force all devices to use specific DNS servers:

```yaml
dns:
  magic_dns: true
  base_domain: vpn.example.com
  override_local_dns: true
  
  nameservers:
    global:
      - 1.1.1.1
      - 1.0.0.1
```

### Split DNS

Route specific domains to specific DNS servers:

```yaml
dns:
  magic_dns: true
  base_domain: vpn.example.com
  
  nameservers:
    global:
      - 1.1.1.1
    
    split:
      internal.company.com:
        - 192.168.1.10
      other.domain.com:
        - 10.0.0.5
```

### Custom DNS Records

Add custom DNS entries for your VPN:

```yaml
dns:
  extra_records:
    - name: "server1.vpn.example.com"
      type: "A"
      value: "100.64.0.10"
    
    - name: "database.vpn.example.com"
      type: "A"
      value: "100.64.0.20"
```

---

## Exit Nodes

Exit nodes route all internet traffic through a specific device in your VPN.

### Configure Exit Node

On the device you want to use as exit node:

```bash
# Enable IP forwarding
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Advertise as exit node
sudo tailscale up --advertise-exit-node
```

### Approve Exit Node

On Headscale server:

```bash
# List routes
headscale routes list

# Enable the exit node route
headscale routes enable -r <route-id>
```

### Use Exit Node

On client devices:

```bash
# List available exit nodes
tailscale exit-node list

# Connect through exit node
tailscale set --exit-node=<node-name>

# Disconnect from exit node
tailscale set --exit-node=
```

---

## Subnet Routing

Allow devices to access networks behind other devices.

### Configure Subnet Router

On the device connected to the subnet:

```bash
# Enable IP forwarding
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Advertise subnet routes
sudo tailscale up --advertise-routes=192.168.1.0/24,10.0.0.0/16
```

### Approve Routes

On Headscale server:

```bash
# List pending routes
headscale routes list

# Enable specific route
headscale routes enable -r <route-id>
```

### Accept Routes on Clients

Clients need to accept advertised routes:

```bash
tailscale up --accept-routes
```

---

## Firewall Configuration

### Hetzner Cloud Firewall (Recommended)

The simplest approach is using Hetzner's built-in firewall:

1. Go to your Hetzner Cloud project
2. Navigate to **Firewalls**
3. Create or edit firewall
4. Add inbound rules:

```
Protocol | Port  | Source    | Description
---------|-------|-----------|------------------
TCP      | 22    | 0.0.0.0/0 | SSH
TCP      | 80    | 0.0.0.0/0 | HTTP (Let's Encrypt)
TCP      | 443   | 0.0.0.0/0 | HTTPS
UDP      | 3478  | 0.0.0.0/0 | STUN
UDP      | 41641 | 0.0.0.0/0 | Tailscale
```

5. Apply to your server

**This is managed from the Hetzner web interface - no server commands needed!**

### UFW (Alternative - if not using Hetzner Firewall)

```bash
# Enable UFW
ufw enable

# Allow SSH (important - don't lock yourself out!)
ufw allow 22/tcp

# Allow HTTP and HTTPS (for Caddy/Let's Encrypt)
ufw allow 80/tcp
ufw allow 443/tcp

# Allow Headscale (if not behind Caddy)
ufw allow 8080/tcp

# Reload
ufw reload

# Check status
ufw status
```

### Firewalld (CentOS/RHEL)

```bash
# Start firewalld
systemctl start firewalld
systemctl enable firewalld

# Allow HTTP and HTTPS
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https

# Reload
firewall-cmd --reload

# Check status
firewall-cmd --list-all
```

### iptables (Advanced)

```bash
# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow Headscale
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

---

## Monitoring and Logs

### Real-time Log Monitoring

```bash
# Follow Headscale logs
journalctl -u headscale -f

# Filter for specific events
journalctl -u headscale | grep "Node connected"

# Show last 100 lines
journalctl -u headscale -n 100
```

### Metrics and Monitoring

Headscale exposes Prometheus metrics on port 9090 (localhost only by default).

To expose metrics:

```yaml
# In /etc/headscale/config.yaml
metrics_listen_addr: 0.0.0.0:9090
```

Access metrics:
```
http://localhost:9090/metrics
```

---

## Backup and Restore

### Backup

```bash
# Create backup directory
mkdir -p /backup/headscale

# Backup database
cp /var/lib/headscale/db.sqlite /backup/headscale/db.sqlite.$(date +%Y%m%d)

# Backup configuration
cp /etc/headscale/config.yaml /backup/headscale/config.yaml.$(date +%Y%m%d)

# Backup ACLs (if using)
cp /etc/headscale/acl.json /backup/headscale/acl.json.$(date +%Y%m%d)
```

### Automated Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backup/headscale"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Stop Headscale
systemctl stop headscale

# Backup
cp /var/lib/headscale/db.sqlite $BACKUP_DIR/db-$DATE.sqlite
cp /etc/headscale/config.yaml $BACKUP_DIR/config-$DATE.yaml

# Restart Headscale
systemctl start headscale

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sqlite" -mtime +30 -delete
find $BACKUP_DIR -name "*.yaml" -mtime +30 -delete
```

### Restore

```bash
# Stop Headscale
systemctl stop headscale

# Restore database
cp /backup/headscale/db-YYYYMMDD.sqlite /var/lib/headscale/db.sqlite

# Restore config
cp /backup/headscale/config-YYYYMMDD.yaml /etc/headscale/config.yaml

# Start Headscale
systemctl start headscale
```

---

## Performance Tuning

### Database Optimization

For SQLite (default):

```yaml
database:
  type: sqlite
  sqlite:
    path: /var/lib/headscale/db.sqlite
    write_ahead_log: true
    wal_autocheckpoint: 1000
```

### Connection Limits

Adjust based on number of devices:

```yaml
# For 100+ devices
server_url: https://vpn.example.com
listen_addr: 0.0.0.0:8080

# Increase if you have many simultaneous connections
ephemeral_node_inactivity_timeout: 30m
```

---

## Security Best Practices

1. **Use strong pre-auth keys**: Generate keys with sufficient entropy
2. **Rotate API keys regularly**: Create new API keys every 90 days
3. **Implement ACLs**: Don't allow all-to-all communication by default
4. **Enable firewall**: Only expose necessary ports
5. **Regular updates**: Keep Headscale and OS updated
6. **Monitor logs**: Watch for suspicious connection attempts
7. **Backup regularly**: Automate database backups
8. **Use HTTPS**: Always use valid TLS certificates

---

For more information, consult the [official Headscale documentation](https://headscale.net/).
