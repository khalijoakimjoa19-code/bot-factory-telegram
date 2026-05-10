# Bot Factory Telegram

## Overview
Telegram bot factory that clones Premium VIP Subscription bots with shared MegaPay account and PostgreSQL database.

## Features

- **Multi-tenant Bot Factory** - Run multiple bot instances from a single factory
- **PostgreSQL Database** - Isolated schemas per bot for clean data separation  
- **MegaPay Integration** - Single MegaPay account serves all bot instances
- **Shared VIP Channel** - All bots manage the same premium channel
- **Factory Admin Access** - Universal admin panel to manage all bots
- **Automated Reminders** - Expiry notifications and subscription management

## Commands

### Factory Commands
- /admin - Factory admin panel
- /clone BOT_TOKEN - Create and start a new bot instance
- /list_bots - View all bot instances
- /delete_bot ID - Remove a bot instance
- /stop_bot ID - Stop a running bot

### Environment Variables

`env
FACTORY_BOT_TOKEN=your_factory_bot_token
FACTORY_ADMIN_ID=8584329987
POSTGRES_DSN=postgresql://user:pass@host:5432/botfactory
MEGAPAY_API_KEY=your_megapay_key
MEGAPAY_EMAIL=your_email@gmail.com
SHARED_CHANNEL_ID=-1003701835008
`

## Deploy to Railway

1. Connect GitHub repository
2. Add PostgreSQL addon
3. Configure environment variables
4. Deploy

## License
MIT
