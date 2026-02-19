# Sync Local and Remote D1 Database

## Current Status
- **Remote D1**: Fully updated with schema and data
- **Local D1**: Needs synchronization

## To Update Local Database

Run these commands from `cloudflare-backend` directory:

```powershell
# 1. Apply schema to local database
npx wrangler d1 execute DB --file=schema-complete.sql

# 2. Apply seed data to local database  
npx wrangler d1 execute DB --file=seed-complete-data.sql
npx wrangler d1 execute DB --file=seed-more-data.sql

# Note: seed-10-patients-complete.sql has foreign key issues, skip for now
```

## Commands Reference

### Local Operations (no --remote flag)
```powershell
# Execute SQL on local database
npx wrangler d1 execute DB --file=schema.sql

# Run local dev server (uses local DB)
npx wrangler dev
```

### Remote Operations (with --remote flag)
```powershell
# Execute SQL on remote D1
npx wrangler d1 execute DB --remote --file=schema.sql

# Deploy Worker to production
npx wrangler deploy
```

### Check Database Content
```powershell
# Query local database
npx wrangler d1 execute DB --command="SELECT COUNT(*) FROM users"

# Query remote database
npx wrangler d1 execute DB --remote --command="SELECT COUNT(*) FROM users"
```

## Why Sync Matters

1. **Local Development**: Test changes locally before deploying to production
2. **Faster Development**: Local database responds instantly
3. **Safe Testing**: Experiment without affecting production data

## Current Database Statistics (Remote)

- **Users**: 10
- **Patients**: 10
- **Doctors**: 4
- **Appointments**: 20+
- **Prescriptions**: 9+
- **Medical Reports**: 11+
- **Bills**: 14+
