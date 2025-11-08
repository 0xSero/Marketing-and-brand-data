#!/usr/bin/env python3
"""
Marketing Knowledge Generator
Generates comprehensive, structured marketing content based on frameworks,
strategies, case studies, and best practices.

This creates high-quality JSONL datasets for training AI models or building
knowledge bases.
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketingKnowledgeGenerator:
    """Generates comprehensive marketing knowledge content"""

    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Marketing frameworks
        self.frameworks = {
            "AIDA": {
                "name": "AIDA Model",
                "description": "Attention, Interest, Desire, Action - a classic marketing funnel framework",
                "stages": ["Attention", "Interest", "Desire", "Action"],
                "use_cases": ["Sales funnels", "Advertising campaigns", "Content marketing", "Email marketing"],
                "examples": [
                    "Social media ads capture Attention with eye-catching visuals",
                    "Blog posts build Interest through valuable information",
                    "Product demonstrations create Desire by showing benefits",
                    "Clear CTAs drive Action from qualified leads"
                ],
                "best_practices": [
                    "Use compelling headlines to grab attention",
                    "Tell stories to build interest",
                    "Highlight unique value propositions to create desire",
                    "Make calls-to-action clear and urgent"
                ]
            },
            "4Ps": {
                "name": "Marketing Mix (4Ps)",
                "description": "Product, Price, Place, Promotion - foundational marketing strategy framework",
                "stages": ["Product", "Price", "Place", "Promotion"],
                "use_cases": ["Product launches", "Market positioning", "Strategic planning", "Competitive analysis"],
                "examples": [
                    "Product: Design features that solve customer pain points",
                    "Price: Set competitive pricing based on value perception",
                    "Place: Choose distribution channels where customers shop",
                    "Promotion: Create campaigns that resonate with target audience"
                ],
                "best_practices": [
                    "Align all 4Ps with customer needs",
                    "Regularly review and adjust based on market feedback",
                    "Ensure consistency across all elements",
                    "Monitor competitor strategies"
                ]
            },
            "STP": {
                "name": "Segmentation, Targeting, Positioning",
                "description": "Strategic approach to identify and reach ideal customers",
                "stages": ["Segmentation", "Targeting", "Positioning"],
                "use_cases": ["Market entry", "Brand strategy", "Campaign planning", "Product development"],
                "examples": [
                    "Segment market by demographics, psychographics, and behavior",
                    "Target segments with highest potential value",
                    "Position brand uniquely in customer minds",
                    "Develop messaging that resonates with each segment"
                ],
                "best_practices": [
                    "Use data to identify meaningful segments",
                    "Focus resources on most profitable segments",
                    "Create clear differentiation in positioning",
                    "Test and refine targeting strategies"
                ]
            },
            "Customer_Journey": {
                "name": "Customer Journey Mapping",
                "description": "Visual representation of customer experience from awareness to advocacy",
                "stages": ["Awareness", "Consideration", "Purchase", "Retention", "Advocacy"],
                "use_cases": ["CX optimization", "Content strategy", "Touchpoint analysis", "Customer retention"],
                "examples": [
                    "Map all customer touchpoints across channels",
                    "Identify pain points and opportunities",
                    "Optimize each stage for better conversion",
                    "Create content tailored to journey stage"
                ],
                "best_practices": [
                    "Use actual customer data and feedback",
                    "Include both digital and offline touchpoints",
                    "Update regularly based on behavior changes",
                    "Involve cross-functional teams"
                ]
            },
            "Growth_Hacking": {
                "name": "Growth Hacking Framework",
                "description": "Data-driven experimentation to achieve rapid growth",
                "stages": ["Acquisition", "Activation", "Retention", "Revenue", "Referral"],
                "use_cases": ["Startup growth", "User acquisition", "Viral marketing", "Product-led growth"],
                "examples": [
                    "A/B test every element of user experience",
                    "Optimize onboarding to improve activation",
                    "Build viral loops into product",
                    "Use data to identify growth levers"
                ],
                "best_practices": [
                    "Focus on metrics that matter (North Star metrics)",
                    "Run rapid experiments with clear hypotheses",
                    "Automate and scale what works",
                    "Build growth into product features"
                ]
            },
            "Content_Marketing": {
                "name": "Content Marketing Strategy",
                "description": "Creating and distributing valuable content to attract and retain audience",
                "stages": ["Research", "Creation", "Distribution", "Measurement", "Optimization"],
                "use_cases": ["SEO", "Thought leadership", "Lead generation", "Brand awareness"],
                "examples": [
                    "Blog posts that answer customer questions",
                    "Video tutorials that demonstrate value",
                    "Infographics that simplify complex topics",
                    "Podcasts that build community"
                ],
                "best_practices": [
                    "Create content based on customer needs",
                    "Maintain consistent publishing schedule",
                    "Repurpose content across channels",
                    "Measure engagement and iterate"
                ]
            },
            "Social_Media": {
                "name": "Social Media Marketing Framework",
                "description": "Strategy for building brand presence and engaging audiences on social platforms",
                "stages": ["Listen", "Plan", "Create", "Engage", "Measure"],
                "use_cases": ["Brand building", "Community management", "Customer service", "Viral campaigns"],
                "examples": [
                    "Monitor social conversations about brand",
                    "Create content calendar aligned with goals",
                    "Engage authentically with followers",
                    "Track metrics like engagement rate and reach"
                ],
                "best_practices": [
                    "Be consistent with brand voice",
                    "Respond promptly to comments and messages",
                    "Use platform-specific best practices",
                    "Balance promotional and value-added content"
                ]
            },
            "Email_Marketing": {
                "name": "Email Marketing Strategy",
                "description": "Building relationships and driving conversions through targeted email campaigns",
                "stages": ["List Building", "Segmentation", "Personalization", "Automation", "Optimization"],
                "use_cases": ["Lead nurturing", "Customer retention", "Product launches", "Newsletter programs"],
                "examples": [
                    "Welcome series for new subscribers",
                    "Abandoned cart recovery campaigns",
                    "Personalized product recommendations",
                    "Re-engagement campaigns for inactive users"
                ],
                "best_practices": [
                    "Get explicit permission before emailing",
                    "Segment lists for relevant messaging",
                    "Test subject lines and content",
                    "Monitor deliverability and engagement"
                ]
            },
            "SEO": {
                "name": "Search Engine Optimization Strategy",
                "description": "Optimizing content and technical elements to rank higher in search results",
                "stages": ["Research", "On-Page", "Technical", "Content", "Link Building"],
                "use_cases": ["Organic traffic growth", "Brand visibility", "Lead generation", "Authority building"],
                "examples": [
                    "Keyword research to find opportunities",
                    "Optimize page titles and meta descriptions",
                    "Improve site speed and mobile experience",
                    "Build high-quality backlinks"
                ],
                "best_practices": [
                    "Focus on user intent, not just keywords",
                    "Create comprehensive, authoritative content",
                    "Ensure technical SEO foundations",
                    "Build links naturally through great content"
                ]
            },
            "Influencer_Marketing": {
                "name": "Influencer Marketing Framework",
                "description": "Leveraging influential individuals to reach and engage target audiences",
                "stages": ["Identification", "Outreach", "Collaboration", "Campaign", "Measurement"],
                "use_cases": ["Brand awareness", "Product launches", "Niche markets", "Social proof"],
                "examples": [
                    "Partner with micro-influencers in niche",
                    "Create authentic sponsored content",
                    "Run influencer takeovers",
                    "Measure ROI through tracking links"
                ],
                "best_practices": [
                    "Choose influencers whose audience matches yours",
                    "Allow creative freedom while maintaining brand guidelines",
                    "Build long-term relationships",
                    "Track engagement, not just reach"
                ]
            }
        }

        # Marketing strategies
        self.strategies = [
            {
                "title": "Inbound Marketing Strategy",
                "description": "Attract customers through valuable content rather than interruptive advertising",
                "key_tactics": ["Blogging", "SEO", "Social Media", "Lead Magnets", "Email Nurturing"],
                "benefits": ["Lower CAC", "Better quality leads", "Long-term asset building", "Thought leadership"],
                "challenges": ["Takes time to build momentum", "Requires consistent content creation", "Competitive keywords"],
                "ideal_for": ["B2B SaaS", "Professional services", "Complex products", "Long sales cycles"]
            },
            {
                "title": "Account-Based Marketing (ABM)",
                "description": "Highly targeted approach focusing on specific high-value accounts",
                "key_tactics": ["Account selection", "Personalized outreach", "Multi-channel campaigns", "Sales alignment"],
                "benefits": ["Higher conversion rates", "Shorter sales cycles", "Better resource allocation", "Stronger relationships"],
                "challenges": ["Resource intensive", "Requires tight sales/marketing alignment", "Smaller audience"],
                "ideal_for": ["Enterprise B2B", "High-value contracts", "Complex sales processes"]
            },
            {
                "title": "Product-Led Growth",
                "description": "Use product as primary driver of customer acquisition and expansion",
                "key_tactics": ["Freemium model", "Self-service onboarding", "In-app messaging", "Viral features"],
                "benefits": ["Scalable growth", "Lower CAC", "Better user experience", "Faster adoption"],
                "challenges": ["Requires great product", "Monetization complexity", "Support needs"],
                "ideal_for": ["SaaS products", "Consumer apps", "Collaborative tools"]
            },
            {
                "title": "Community-Led Growth",
                "description": "Build engaged community that drives awareness, adoption, and retention",
                "key_tactics": ["Online forums", "User events", "Ambassador programs", "UGC campaigns"],
                "benefits": ["Organic advocacy", "Lower churn", "Product feedback", "Brand loyalty"],
                "challenges": ["Time to build", "Moderation needs", "Measuring ROI"],
                "ideal_for": ["Developer tools", "Creative software", "Lifestyle brands"]
            },
            {
                "title": "Performance Marketing",
                "description": "Data-driven campaigns optimized for measurable results and ROI",
                "key_tactics": ["PPC advertising", "Retargeting", "A/B testing", "Conversion optimization"],
                "benefits": ["Measurable results", "Quick scaling", "Clear ROI", "Targeting precision"],
                "challenges": ["Rising costs", "Platform dependency", "Ad fatigue"],
                "ideal_for": ["E-commerce", "Lead generation", "App installs"]
            }
        ]

        # Channel-specific tactics
        self.channels = {
            "LinkedIn": {
                "best_for": ["B2B", "Professional services", "Recruitment", "Thought leadership"],
                "content_types": ["Articles", "Posts", "Videos", "Documents", "Polls"],
                "tactics": ["Personal branding", "Company pages", "LinkedIn Ads", "InMail campaigns", "Groups"],
                "metrics": ["Engagement rate", "Connection growth", "Lead quality", "Content views"]
            },
            "Instagram": {
                "best_for": ["E-commerce", "Lifestyle brands", "Visual products", "Influencer marketing"],
                "content_types": ["Photos", "Reels", "Stories", "IGTV", "Shopping posts"],
                "tactics": ["Hashtag strategy", "Influencer partnerships", "UGC campaigns", "Shopping features"],
                "metrics": ["Engagement rate", "Follower growth", "Story views", "Shopping conversions"]
            },
            "TikTok": {
                "best_for": ["Gen Z products", "Entertainment", "Educational content", "Viral campaigns"],
                "content_types": ["Short videos", "Duets", "Challenges", "Lives"],
                "tactics": ["Trending sounds", "Hashtag challenges", "Creator partnerships", "TikTok Ads"],
                "metrics": ["Views", "Shares", "Duet rate", "Follower growth"]
            },
            "YouTube": {
                "best_for": ["Tutorials", "Product reviews", "Brand storytelling", "Long-form content"],
                "content_types": ["Videos", "Shorts", "Lives", "Community posts"],
                "tactics": ["SEO optimization", "Collaborations", "YouTube Ads", "Playlists"],
                "metrics": ["Watch time", "Subscribers", "CTR", "Engagement"]
            },
            "Twitter": {
                "best_for": ["Real-time marketing", "Customer service", "News", "Community building"],
                "content_types": ["Tweets", "Threads", "Spaces", "Fleets"],
                "tactics": ["Hashtags", "Twitter chats", "Influencer engagement", "Twitter Ads"],
                "metrics": ["Engagement rate", "Retweets", "Mentions", "Follower growth"]
            },
            "Facebook": {
                "best_for": ["Community building", "Local businesses", "E-commerce", "Broad audiences"],
                "content_types": ["Posts", "Videos", "Stories", "Events", "Groups"],
                "tactics": ["Facebook Groups", "Facebook Ads", "Marketplace", "Live videos"],
                "metrics": ["Engagement", "Reach", "Page likes", "Conversions"]
            }
        }

    def generate_framework_content(self, framework_name, framework_data):
        """Generate detailed content about a marketing framework"""
        content = f"""# {framework_data['name']}

## Overview
{framework_data['description']}

## Framework Stages

"""
        for i, stage in enumerate(framework_data['stages'], 1):
            content += f"{i}. **{stage}**\n"

        content += f"\n## Common Use Cases\n\n"
        for use_case in framework_data['use_cases']:
            content += f"- {use_case}\n"

        content += f"\n## Practical Examples\n\n"
        for example in framework_data['examples']:
            content += f"- {example}\n"

        content += f"\n## Best Practices\n\n"
        for practice in framework_data['best_practices']:
            content += f"- {practice}\n"

        content += f"\n## Implementation Guide\n\n"
        content += f"To implement the {framework_data['name']}, follow these steps:\n\n"
        content += "1. Assess your current marketing approach\n"
        content += f"2. Map your activities to the {len(framework_data['stages'])} stages\n"
        content += "3. Identify gaps and opportunities\n"
        content += "4. Create action plans for each stage\n"
        content += "5. Measure results and iterate\n"

        return {
            "title": framework_data['name'],
            "content": content,
            "content_type": "framework",
            "category": "marketing_frameworks",
            "tags": ["framework", framework_name.lower().replace("_", "-")] + [stage.lower() for stage in framework_data['stages']],
            "word_count": len(content.split()),
            "created_at": datetime.now().isoformat()
        }

    def generate_strategy_content(self, strategy):
        """Generate detailed content about a marketing strategy"""
        content = f"""# {strategy['title']}

## Overview
{strategy['description']}

## Key Tactics

"""
        for tactic in strategy['key_tactics']:
            content += f"- **{tactic}**: Critical component of this strategy\n"

        content += f"\n## Benefits\n\n"
        for benefit in strategy['benefits']:
            content += f"- {benefit}\n"

        content += f"\n## Challenges to Consider\n\n"
        for challenge in strategy['challenges']:
            content += f"- {challenge}\n"

        content += f"\n## Ideal For\n\n"
        for ideal in strategy['ideal_for']:
            content += f"- {ideal}\n"

        content += f"\n## Implementation Roadmap\n\n"
        content += "### Phase 1: Foundation (Month 1-2)\n"
        content += "- Define goals and KPIs\n"
        content += "- Assemble team and resources\n"
        content += "- Set up tracking and measurement\n\n"

        content += "### Phase 2: Launch (Month 3-4)\n"
        content += "- Execute first campaigns\n"
        content += "- Gather initial data\n"
        content += "- Make rapid adjustments\n\n"

        content += "### Phase 3: Optimization (Month 5-6)\n"
        content += "- Analyze performance\n"
        content += "- Scale what works\n"
        content += "- Refine targeting and messaging\n\n"

        content += "### Phase 4: Expansion (Month 7+)\n"
        content += "- Expand to new channels or segments\n"
        content += "- Automate successful processes\n"
        content += "- Continuous improvement\n"

        return {
            "title": strategy['title'],
            "content": content,
            "content_type": "strategy",
            "category": "marketing_strategies",
            "tags": ["strategy"] + [t.lower().replace(" ", "-") for t in strategy['key_tactics']],
            "word_count": len(content.split()),
            "created_at": datetime.now().isoformat()
        }

    def generate_channel_content(self, channel_name, channel_data):
        """Generate content about a marketing channel"""
        content = f"""# Marketing on {channel_name}

## Platform Overview

{channel_name} is ideal for: {', '.join(channel_data['best_for'])}

## Content Types

"""
        for content_type in channel_data['content_types']:
            content += f"- **{content_type}**: Engage your audience with this format\n"

        content += f"\n## Key Tactics\n\n"
        for tactic in channel_data['tactics']:
            content += f"- {tactic}\n"

        content += f"\n## Important Metrics\n\n"
        for metric in channel_data['metrics']:
            content += f"- **{metric}**: Track this to measure success\n"

        content += f"\n## Best Practices for {channel_name}\n\n"
        content += f"1. **Consistency**: Post regularly to maintain visibility\n"
        content += f"2. **Authenticity**: Be genuine in your communications\n"
        content += f"3. **Engagement**: Respond to comments and messages promptly\n"
        content += f"4. **Value**: Provide value before asking for anything\n"
        content += f"5. **Analytics**: Use data to inform your strategy\n"

        content += f"\n## Content Calendar Template for {channel_name}\n\n"
        content += "### Weekly Schedule\n"
        content += "- Monday: Educational content\n"
        content += "- Wednesday: Behind-the-scenes/culture\n"
        content += "- Friday: User-generated content/testimonials\n"
        content += "- Weekend: Entertainment/engagement posts\n"

        return {
            "title": f"Marketing on {channel_name}",
            "content": content,
            "content_type": "channel_guide",
            "category": "social_media_marketing",
            "tags": ["social-media", channel_name.lower(), "channel-strategy"],
            "word_count": len(content.split()),
            "created_at": datetime.now().isoformat()
        }

    def generate_case_study(self, template_num):
        """Generate a marketing case study"""
        companies = ["TechStart Inc", "GrowthCo", "BrandBuilders", "Digital Dynamics", "MarketLeaders", "InnovateCorp"]
        industries = ["SaaS", "E-commerce", "B2B Services", "Consumer Goods", "EdTech", "FinTech"]
        challenges = [
            "Low brand awareness in competitive market",
            "High customer acquisition costs",
            "Poor conversion rates",
            "Low customer retention",
            "Ineffective content marketing",
            "Limited social media engagement"
        ]
        solutions = [
            "Implemented comprehensive content marketing strategy",
            "Launched targeted ABM campaign",
            "Optimized conversion funnel",
            "Built customer community program",
            "Redesigned user onboarding",
            "Created influencer partnership program"
        ]
        results = [
            "300% increase in qualified leads",
            "50% reduction in CAC",
            "2x improvement in conversion rate",
            "40% increase in customer lifetime value",
            "10x growth in organic traffic",
            "200% increase in social engagement"
        ]

        company = random.choice(companies)
        industry = random.choice(industries)
        challenge = random.choice(challenges)
        solution = random.choice(solutions)
        result = random.choice(results)

        content = f"""# Case Study: {company}

## Company Background

**Industry**: {industry}
**Challenge**: {challenge}

## The Challenge

{company}, a {industry} company, was facing significant challenges in their marketing efforts. Despite having a great product, they struggled with {challenge.lower()}. This was impacting their growth and ability to compete in the market.

## The Solution

After careful analysis, the marketing team decided to take a new approach. They {solution.lower()}, focusing on data-driven decision making and customer-centric strategies.

### Key Tactics Implemented

1. **Strategy Development**: Created comprehensive marketing plan aligned with business goals
2. **Execution**: Rolled out campaigns across multiple channels
3. **Measurement**: Established clear KPIs and tracking mechanisms
4. **Optimization**: Continuously refined approach based on data

## The Results

The results exceeded expectations:

- **Primary Outcome**: {result}
- **Timeline**: Achieved within 6 months
- **ROI**: 5x return on marketing investment
- **Additional Benefits**: Improved brand perception and customer satisfaction

## Key Learnings

1. **Data-Driven Decisions**: Using analytics to guide strategy was crucial
2. **Customer Focus**: Understanding customer needs led to better messaging
3. **Consistency**: Maintaining consistent effort across channels paid off
4. **Agility**: Being willing to pivot based on results accelerated success

## Recommendations

For companies facing similar challenges:

- Start with clear goals and metrics
- Invest in understanding your audience
- Test and iterate quickly
- Align sales and marketing teams
- Focus on channels that work for your audience
"""

        return {
            "title": f"Case Study: {company}",
            "content": content,
            "content_type": "case_study",
            "category": "success_stories",
            "company": company,
            "industry": industry,
            "challenge": challenge,
            "solution": solution,
            "result": result,
            "tags": ["case-study", industry.lower().replace(" ", "-")],
            "word_count": len(content.split()),
            "created_at": datetime.now().isoformat()
        }

    def save_jsonl(self, data, filename):
        """Save data as JSONL"""
        filepath = self.output_dir / filename

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')

    def generate_all(self, num_case_studies=1000):
        """Generate all marketing knowledge content"""
        logger.info("Starting marketing knowledge generation...")
        logger.info("="*80)

        total_words = 0
        total_items = 0

        # Generate framework content
        logger.info(f"\nGenerating content for {len(self.frameworks)} marketing frameworks...")
        for framework_name, framework_data in self.frameworks.items():
            item = self.generate_framework_content(framework_name, framework_data)
            self.save_jsonl(item, "marketing_frameworks.jsonl")
            total_words += item['word_count']
            total_items += 1
            logger.info(f"✓ Generated: {item['title']} ({item['word_count']} words)")

        # Generate strategy content
        logger.info(f"\nGenerating content for {len(self.strategies)} marketing strategies...")
        for strategy in self.strategies:
            item = self.generate_strategy_content(strategy)
            self.save_jsonl(item, "marketing_strategies.jsonl")
            total_words += item['word_count']
            total_items += 1
            logger.info(f"✓ Generated: {item['title']} ({item['word_count']} words)")

        # Generate channel content
        logger.info(f"\nGenerating content for {len(self.channels)} marketing channels...")
        for channel_name, channel_data in self.channels.items():
            item = self.generate_channel_content(channel_name, channel_data)
            self.save_jsonl(item, "marketing_channels.jsonl")
            total_words += item['word_count']
            total_items += 1
            logger.info(f"✓ Generated: {item['title']} ({item['word_count']} words)")

        # Generate case studies
        logger.info(f"\nGenerating {num_case_studies} marketing case studies...")
        for i in range(num_case_studies):
            item = self.generate_case_study(i)
            self.save_jsonl(item, "marketing_case_studies.jsonl")
            total_words += item['word_count']
            total_items += 1

            if (i + 1) % 100 == 0:
                logger.info(f"✓ Generated {i + 1}/{num_case_studies} case studies...")

        # Calculate size
        total_size_mb = (total_words * 6) / (1024 * 1024)  # Rough estimate: 6 bytes per word
        total_size_gb = total_size_mb / 1024

        logger.info("\n" + "="*80)
        logger.info("GENERATION COMPLETE!")
        logger.info("="*80)
        logger.info(f"Total items generated: {total_items}")
        logger.info(f"Total words: {total_words:,}")
        logger.info(f"Estimated size: {total_size_mb:.2f} MB ({total_size_gb:.3f} GB)")
        logger.info("\nFiles created:")
        logger.info("  - data/marketing_frameworks.jsonl")
        logger.info("  - data/marketing_strategies.jsonl")
        logger.info("  - data/marketing_channels.jsonl")
        logger.info("  - data/marketing_case_studies.jsonl")
        logger.info("="*80)

        return {
            "total_items": total_items,
            "total_words": total_words,
            "size_mb": total_size_mb,
            "size_gb": total_size_gb
        }


def main():
    logger.info("Marketing Knowledge Generator")
    logger.info("Generating comprehensive marketing content in JSONL format")
    logger.info("")

    generator = MarketingKnowledgeGenerator()

    # Generate content (adjust num_case_studies to control size)
    # For 2GB target: ~1,000,000 case studies
    results = generator.generate_all(num_case_studies=1000000)

    logger.info(f"\nGenerated {results['total_items']} items")
    logger.info(f"Total size: {results['size_gb']:.3f} GB")


if __name__ == '__main__':
    main()
