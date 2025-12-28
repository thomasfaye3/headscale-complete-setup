# Frequently Asked Questions (FAQ)

Common questions and answers about Headscale installation and usage.

## General Questions

### What is the difference between Headscale and Tailscale?

**Tailscale** is a commercial VPN service that provides:
- Managed control server
- Easy setup
- Support
- Some features require paid plans

**Headscale** is:
- Open-source alternative to Tailscale's control server
- Self-hosted (you run your own server)
- Free with unlimited devices
- Compatible with Tailscale clients
- Requires technical knowledge to set up

### Do I need to pay for Tailscale to use Headscale?

No! Headscale is completely free and open-source. You only use the free Tailscale **clients** (apps) but connect them to your own Headscale server instead of Tailscale's servers.

### Is Headscale secure?

Yes, when properly configured:
- Uses WireGuard protocol (same as Tailscale)
- End-to-end encryption
- Your data never goes through third-party servers
- You control all aspects of your network

However, security depends on:
- Keeping your server updated
- Using strong authentication
- Properly configuring ACLs
- Securing your VPS

---

## Installation Questions

### Which VPS provider should I use?

Any provider works! Popular choices:
- **Hetzner Cloud**: Good performance, fair pricing, EU-based
- **DigitalOcean**: Easy to use, good documentation
- **Vultr**: Competitive pricing, many locations
- **Linode**: Reliable, good support
- **Oracle Cloud**: Free tier available (limited capacity)

Requirements: 2GB RAM, 1 vCPU, 20GB storage

### Can I use a Raspberry Pi instead of a VPS?

Yes! Headscale runs well on Raspberry Pi:
- Use ARM version of Headscale
- Ensure stable internet connection
- Configure port forwarding on your router
- Consider using DynamicDNS if you don't have static IP

### Do I need a domain name?

**Recommended but not required:**
- With domain: Easy HTTPS with Let's Encrypt, professional setup
- Without domain: Can use IP address, but:
  - No automatic HTTPS
  - Need to trust self-signed certificates
  - Less convenient for users

Free options: DuckDNS, FreeDNS, No-IP

### Can I use Cloudflare proxy (orange cloud)?

**No!** Cloudflare proxy blocks WebSocket connections required by Tailscale protocol.

Always use **DNS-only mode** (gray cloud) for your Headscale domain.

---

## Configuration Questions

### How many devices can I connect?

Unlimited! Unlike Tailscale's free tier (100 devices max), Headscale has no device limit.

Performance depends on your VPS specs:
- 2GB RAM: 100+ devices easily
- 4GB RAM: 500+ devices
- For 1000+ devices: Consider more resources or database optimization

### Can I use PostgreSQL instead of SQLite?

Yes, but **not recommended**. Headscale developers optimize for SQLite:
- SQLite is faster for most use cases
- PostgreSQL support is legacy only
- SQLite is simpler to manage and backup

### How do I update Headscale?

```bash
# Download new version
wget https://github.com/juanfont/headscale/releases/download/vX.X.X/headscale_X.X.X_linux_amd64.deb

# Stop service
systemctl stop headscale

# Backup database
cp /var/lib/headscale/db.sqlite /var/lib/headscale/db.sqlite.backup

# Install update
dpkg -i headscale_X.X.X_linux_amd64.deb

# Start service
systemctl start headscale

# Check status
systemctl status headscale
```

### Can I migrate from Tailscale to Headscale?

Not directly. You need to:
1. Set up Headscale server
2. Disconnect devices from Tailscale
3. Reconnect them to your Headscale server

Note: You'll lose Tailscale-specific features like MagicDNS history.

---

## Usage Questions

### How do I connect my phone/tablet?

**Android:**
1. Install Tailscale from Play Store
2. Open app → Settings → Use custom control server
3. Enter your Headscale URL
4. Use pre-auth key to connect

**iOS:**
1. Install Tailscale from App Store
2. Settings → Use custom control server
3. Enter your Headscale URL
4. Use pre-auth key to connect

### Can multiple users share the same Headscale server?

Yes! Create separate users for different people/organizations:

```bash
headscale users create company-a
headscale users create company-b
```

Each user gets their own:
- Pre-auth keys
- Device namespace
- ACL policies (if configured)

### How do I remove a device?

**Via CLI:**
```bash
# List devices
headscale nodes list

# Delete specific device
headscale nodes delete -i <node-id>
```

**Via Web Interface:**
1. Go to Nodes
2. Find device
3. Click delete button

**Note:** Device will be unable to connect until re-authenticated.

### Can I access my home network from anywhere?

Yes! Set up **subnet routing**:
1. Configure one device as subnet router
2. Advertise your home network (e.g., 192.168.1.0/24)
3. Approve route in Headscale
4. Clients can access your home network devices

See ADVANCED.md for details.

---

## Troubleshooting Questions

### Devices connect but can't communicate

Check:
1. **Firewall**: Devices might block Tailscale traffic
2. **ACLs**: Check if policies block communication
3. **IP forwarding**: Might be needed for subnet routing
4. **NAT traversal**: Some networks block P2P connections

### Web interface shows authentication error

Common causes:
1. **Wrong API key**: Regenerate key on server
2. **Wrong URL**: Must match your Headscale server URL
3. **Container not running**: Check Docker status
4. **Caddy misconfigured**: Check reverse proxy settings

### Certificate errors when connecting

Causes:
1. **Let's Encrypt not working**: Check Caddy logs
2. **DNS not updated**: Verify domain points to VPS IP
3. **Firewall blocking**: Allow ports 80 and 443
4. **Cloudflare proxy enabled**: Disable orange cloud

### Devices frequently disconnect

Possible reasons:
1. **VPS resource limits**: Check CPU/RAM usage
2. **Network issues**: VPS connectivity problems
3. **Timeout too short**: Adjust ephemeral_node_inactivity_timeout
4. **Client app issues**: Update Tailscale client

---

## Performance Questions

### Is Headscale slower than Tailscale?

No! Performance is identical because:
- Same WireGuard protocol
- Same client applications
- Direct P2P connections between devices
- Control server only coordinates connections

Your VPS only handles:
- Initial authentication
- Connection coordination
- Route updates

Actual traffic goes directly between devices.

### Does my VPS need lots of bandwidth?

No! VPS bandwidth usage is minimal:
- ~1KB per device per minute (heartbeat)
- Initial connection setup: ~10KB
- No actual data traffic goes through VPS

For 100 devices: ~100MB/month

### How much does it cost to run Headscale?

**VPS costs (monthly):**
- Hetzner CX22: ~€4
- DigitalOcean Basic: $4
- Vultr: $3.50-6
- Oracle Free Tier: $0 (if available)

**Plus:**
- Domain: ~$10-15/year (optional)

**Total:** ~$4-5/month or less

---

## Feature Questions

### Does Headscale support MagicDNS?

Yes! MagicDNS works with Headscale:
- Devices get friendly names (device-name.vpn.example.com)
- Works automatically after configuration
- Configure in config.yaml

### Can I use Headscale as exit node?

Yes! Any device in your Headscale network can be an exit node:
1. Enable on device: `tailscale up --advertise-exit-node`
2. Approve on server: `headscale routes enable -r <route-id>`
3. Use on clients: `tailscale set --exit-node=<node>`

### Does Headscale support Taildrop?

**Not officially**. Taildrop is Tailscale-specific and requires their servers.

Alternatives:
- Use file sharing over VPN (SMB, NFS, etc.)
- Set up Nextcloud/Syncthing on VPN
- Use rsync/scp over VPN

### Can I use custom DERP servers?

Yes! You can run your own DERP relay servers:
- Useful for geographically distributed teams
- Improves performance when P2P fails
- See Headscale documentation for setup

---

## Legal & Privacy Questions

### Is self-hosting Headscale legal?

Yes! Headscale is open-source (BSD 3-Clause license) and legal to use.

**However:**
- Respect VPS provider's terms of service
- Don't use for illegal activities
- Follow local data protection laws

### Does Headscale collect my data?

No! When you self-host:
- You control all data
- No telemetry by default
- No third-party access
- Logs stored on your server

### GDPR compliance?

Self-hosting Headscale can **help** with GDPR:
- Full data control
- No data sharing with third parties
- Ability to delete data on request

**But:**
- You're responsible for compliance
- Implement proper security measures
- Keep logs of data processing
- Consult legal expert if handling sensitive data

---

## Need More Help?

- **Headscale Documentation**: https://headscale.net/
- **GitHub Issues**: https://github.com/juanfont/headscale/issues
- **Headscale Discord**: https://discord.gg/c84AZQhmpx
- **Tailscale Docs** (client usage): https://tailscale.com/kb/

---

*Last updated: December 2025*
