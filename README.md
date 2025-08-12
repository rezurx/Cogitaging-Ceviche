# The Cogitating Ceviche
## Modern Hugo-Based Satirical Blog with AI Development Integration

**Live Site**: https://darkorange-lark-300659.hostingersite.com  
**Author**: Conrad T. Hannon (pseudonym)  
**Status**: ✅ Live & AI-Enhanced

---

## Project Overview

The Cogitating Ceviche is a professional Hugo-based static blog featuring satirical commentary on AI, politics, culture, and modern society. The site aggregates external articles from Medium, Substack, and Vocal Media, presenting them in a modern Medium-style grid layout.

### Key Features
- **Modern Design**: Responsive Medium-style grid layout with professional typography
- **Multi-Platform Content**: Aggregates articles from Medium, Substack, and Vocal Media
- **SEO Optimized**: Canonical URLs, meta tags, and structured data
- **Performance Focused**: Static site generation with optimized loading
- **AI-Enhanced Development**: Integrated CC-Subagents for intelligent assistance

---

## Technology Stack

### Core Technologies
- **Static Site Generator**: Hugo v0.132+
- **Theme**: Ananke (customized)
- **Content Format**: Markdown with YAML frontmatter
- **Hosting**: Hostinger
- **Domain**: darkorange-lark-300659.hostingersite.com

### AI Development Integration
- **CC-Subagents System**: Universal AI development assistant framework
- **Specialized Agents**: 6 domain-specific Claude Code subagents
- **Development Environment**: Python virtual environment with dependencies

---

## Project Structure

```
cogitating-ceviche/
├── content/
│   └── external-articles/           # Blog posts aggregated from external sources
├── themes/ananke/                   # Hugo theme (customized)
├── layouts/
│   └── index.html                   # Custom homepage with grid layout
├── static/                          # Static assets
├── public/                          # Generated site (build output)
├── .claude/
│   └── agents/                      # AI subagent configurations
├── subagent-env/                    # Python virtual environment
├── claude_subagent_manager.py       # AI agent management system
├── activate_subagents.sh            # Quick activation script
├── ingest_external_articles.py      # Content automation script
└── hugo.toml                        # Site configuration
```

---

## AI Development Capabilities

### Installed Subagents (6 Total)

#### Core Development
- **`hugo-specialist`**: Hugo static site expert for blog optimization
- **`content-manager`**: SEO and editorial workflow specialist
- **`documentation-generator`**: Technical documentation expert
- **`python-specialist`**: Python development and automation

#### Quality Assurance (Proactive)
- **`code-reviewer`** ⚡: Automatic code review and quality checking
- **`test-runner`** ⚡: Automatic test execution and failure resolution

### Usage Examples
```bash
# Activate AI development environment
./activate_subagents.sh

# Use subagents in Claude Code with natural language:
"Use the hugo-specialist to optimize site performance"
"Use the content-manager to improve article SEO"
"Use the hugo-specialist to create a new article template"
```

---

## Development Workflow

### Content Management
1. **External Content Ingestion**: `python3 ingest_external_articles.py`
2. **Site Generation**: `hugo` (builds to `public/`)
3. **Local Development**: `hugo server` (serves on localhost:1313)
4. **Deployment**: Manual upload to Hostinger via SSH/File Manager

### AI-Assisted Development
1. **Activate Environment**: `./activate_subagents.sh`
2. **Use Specialized Agents**: Natural language commands in Claude Code
3. **Proactive Quality**: Automatic code review and testing
4. **Documentation**: AI-generated project documentation

---

## Site Features

### Design & User Experience
- **Responsive Grid Layout**: Auto-fit columns with 350px minimum width
- **Professional Cards**: Shadow effects, hover animations, rounded corners
- **Typography**: Charter/Georgia serif fonts for readability
- **Source Attribution**: Color-coded platform badges (Medium, Substack, Vocal)
- **Image Integration**: Real article thumbnails from original sources

### Content Features
- **Multi-Platform Aggregation**: Automatically pulls from RSS feeds
- **Consistent Previews**: ~100-word summaries for all articles
- **Direct Linking**: Original article links preserved
- **Metadata Rich**: Author, publish date, source platform
- **SEO Optimized**: Proper meta tags and canonical URLs

### Performance Features
- **Static Generation**: Fast loading with no database
- **Optimized Images**: Proper sizing and lazy loading
- **Minimal JavaScript**: Lightweight interactive elements
- **CSS Optimization**: Minified and bundled stylesheets

---

## Deployment Information

### Live Deployment
- **URL**: https://darkorange-lark-300659.hostingersite.com
- **Hosting**: Hostinger shared hosting
- **SSL**: Enabled (Let's Encrypt)
- **Build Process**: Hugo → Upload to `public_html/`

### Development Environment
- **Local Development**: Hugo server (when localhost is accessible)
- **Content Testing**: Local Hugo builds for verification
- **AI Integration**: CC-Subagents system for development assistance

---

## Content Strategy

### External Article Sources
1. **Medium**: @conradthannon - Primary satirical content
2. **Substack**: conradthannon.substack.com - Newsletter essays  
3. **Vocal Media**: Conrad T. Hannon - Extended articles

### Content Themes
- **AI & Technology**: Commentary on artificial intelligence and tech culture
- **Political Satire**: Satirical takes on current events and politics
- **Cultural Analysis**: Modern society and cultural trends
- **Historical Perspectives**: History through a satirical lens

### SEO Strategy
- **Author Authority**: Building Conrad T. Hannon as recognized pseudonym
- **Canonical URLs**: Proper attribution to original sources
- **Long-tail Keywords**: Targeting specific satirical and commentary niches
- **Content Freshness**: Regular RSS-based content updates

---

## Getting Started

### Prerequisites
- Hugo v0.132 or later
- Python 3.8+ (for content automation and AI agents)
- Git (for version control)

### Setup Instructions

1. **Clone Repository** (if applicable)
   ```bash
   git clone <repository-url>
   cd cogitating-ceviche
   ```

2. **Install Hugo Dependencies**
   ```bash
   hugo mod get
   ```

3. **Set Up AI Development Environment**
   ```bash
   ./activate_subagents.sh
   ```

4. **Generate Site**
   ```bash
   hugo
   ```

5. **Local Development**
   ```bash
   hugo server
   ```

### Content Updates
```bash
# Update external articles
python3 ingest_external_articles.py

# Rebuild site
hugo

# Deploy (manual upload to hosting)
```

---

## Documentation

### Project Documentation
- **`DEPLOYMENT_PROGRESS.md`**: Complete deployment history and technical details
- **`progress.md`**: Development progress tracker with major milestones
- **`CC_SUBAGENTS_IMPLEMENTATION.md`**: AI development system documentation
- **Site Build Spec**: Original requirements and SEO strategy

### Configuration Files
- **`hugo.toml`**: Hugo site configuration
- **`requirements.txt`**: Python dependencies for automation
- **`.claude/agents/*.md`**: AI subagent configurations

---

## Maintenance

### Regular Tasks
- **Content Updates**: RSS ingestion and new article processing
- **Theme Updates**: Hugo theme and template maintenance
- **SEO Monitoring**: Performance and ranking tracking
- **Security Updates**: Hugo and dependency updates

### AI Agent Maintenance
- **Agent Updates**: Refining subagent configurations as needed
- **New Agents**: Adding specialized agents for new requirements
- **Environment Updates**: Python dependency management

---

## Support & Troubleshooting

### Common Issues
- **Hugo Build Errors**: Check `hugo.toml` configuration and theme compatibility
- **Content Ingestion**: Verify RSS feed URLs and network connectivity
- **Deployment Issues**: Check Hostinger file structure and permissions
- **AI Agent Issues**: Ensure virtual environment is activated

### Quick Fixes
```bash
# Reset Hugo caches
hugo mod clean

# Reinstall AI dependencies
source subagent-env/bin/activate && pip install -r requirements.txt

# Rebuild everything
rm -rf public/ resources/ && hugo
```

---

## Contributing

This is a personal blog project for Conrad T. Hannon's satirical content. The AI development system can be extended for:

- **New Content Sources**: Additional RSS feed integration
- **Design Enhancements**: Theme customization and new layouts  
- **Automation Features**: Enhanced content processing and scheduling
- **SEO Improvements**: Advanced optimization and analytics

---

## License & Attribution

- **Content**: © Conrad T. Hannon (satirical pseudonym)
- **Hugo Theme**: Ananke theme (modified)
- **CC-Subagents**: Universal AI development system integration
- **External Content**: Properly attributed to original sources with canonical URLs

---

**Project Status**: 🎨 Brand Integration In Progress - Core Functionality Complete  
**Last Updated**: August 12, 2025

## 🚨 **Current Issues (For Next Session):**
- **Fish logo not displaying** in header despite correct configuration
- **Left margin not applied** - page still flush against left edge  
- **Header link issues** - may be redirecting incorrectly
- **Title font** not changing to serif despite CSS rules
- **Article previews not working** - still showing promotional text instead of 100-word content previews

## ✅ **Completed This Session:**
- Fixed GitHub Actions PyYAML dependency issue (automation now working)
- Implemented comprehensive brand color palette (fish blue, glasses yellow, etc.)
- Created branded card styling with fish blue borders and golden accents
- Enhanced article preview scraper logic (needs debugging - not working yet)
- Updated template to 100-word article previews (needs verification)
- Added new content ingestion capabilities