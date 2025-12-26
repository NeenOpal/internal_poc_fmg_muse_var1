"""
Ideal conversation examples for evaluating and guiding email generation.

These serve as few-shot examples that the LLM can reference during generation
to produce higher quality, more consistent emails.

Structure:
- Each conversation represents an ideal interaction flow
- Conversations can be single-turn (request -> email) or multi-turn (with refinements)
- Tags and metadata enable retrieval of relevant examples during generation
"""

from typing import Optional
from app.models.email import PurposeEnum, ToneEnum, LengthEnum


# =============================================================================
# CONVERSATION MESSAGE TYPES
# =============================================================================
# These help categorize what kind of message it is for retrieval and evaluation

MESSAGE_TYPES = {
    "initial_request": "User's first request for an email",
    "refinement_request": "User asking to modify a generated email",
    "clarification_question": "Assistant asking for more details",
    "clarification_response": "User providing requested details",
    "email_generation": "Assistant's email response",
    "email_refinement": "Assistant's refined email response",
}


# =============================================================================
# IDEAL CONVERSATIONS
# =============================================================================
# Each conversation contains:
# - id: Unique identifier for the conversation
# - purpose: Email purpose category
# - tone: Target tone
# - length: Target length
# - scenario: Brief description of the situation (used for retrieval)
# - tags: Keywords for semantic matching (used for retrieval)
# - conversation: List of messages in order
# - evaluation_notes: What makes this conversation ideal

IDEAL_CONVERSATIONS = [
    # =========================================================================
    # 1. RELATIONSHIP BUILDER - Professional, Medium (Single-turn)
    # =========================================================================
    {
        "id": "TC001",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Thanking a long-term client for 10 years of partnership",
        "tags": ["anniversary", "thank you", "appreciation", "long-term client", "milestone", "10 years"],
        "conversation": [
            {
                "role": "user",
                "content": "Thank a long-term client for their continued trust after 10 years",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Celebrating 10 Years of Partnership",
                "email_body": """Hi [Recipient Name],

As we mark ten years of working together, I wanted to take a moment to express my sincere gratitude for your continued trust and partnership.

Over the past decade, we've navigated various market conditions together, and I've valued every conversation we've had about your financial goals. Your thoughtful approach to planning and your openness to discussing both opportunities and concerns have made our work together truly rewarding.

I remain committed to helping you pursue your financial objectives while managing risk appropriately. As always, please don't hesitate to reach out if you have any questions or would like to discuss any aspect of your portfolio.

Thank you again for allowing me to be part of your financial journey.

Best regards,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Warm but professional tone",
            "No performance promises or guarantees",
            "Acknowledges partnership without overpromising",
            "Clear placeholders for personalization",
            "Appropriate length for medium setting",
        ],
    },

    # =========================================================================
    # 2. EDUCATIONAL CONTENT - Professional, Long (Single-turn)
    # =========================================================================
    {
        "id": "TC002",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.LONG,
        "scenario": "Explaining dollar-cost averaging to nervous clients during volatility",
        "tags": ["dollar-cost averaging", "DCA", "volatility", "investment strategy", "nervous clients", "market fluctuations", "education"],
        "conversation": [
            {
                "role": "user",
                "content": "Explain dollar-cost averaging to clients who are nervous about market volatility",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Understanding Dollar-Cost Averaging: A Strategy for Uncertain Markets",
                "email_body": """Hi [Recipient Name],

Given recent market fluctuations, I wanted to share some information about dollar-cost averaging (DCA), a strategy that many investors find helpful during periods of uncertainty.

Dollar-cost averaging involves investing a fixed amount at regular intervals, regardless of market conditions. For example, investing $500 monthly rather than $6,000 as a lump sum. This approach has several potential benefits worth considering.

First, DCA may help reduce the impact of short-term volatility on your overall investment. By purchasing at various price points over time, you potentially avoid the risk of investing a large sum at an unfavorable moment. When prices are lower, your fixed investment buys more shares; when prices are higher, it buys fewer.

Second, this strategy can help remove emotion from investment decisions. Rather than trying to time market highs and lows—something even professional investors struggle with—you maintain a consistent approach.

However, it's important to understand that dollar-cost averaging does not guarantee profits or protect against losses in declining markets. All investments carry risk, including the potential loss of principal. Historical performance of any strategy does not guarantee future results.

Whether DCA aligns with your goals depends on your individual circumstances, time horizon, and risk tolerance. I'd be happy to discuss how this approach might fit into your overall financial plan.

Please feel free to reach out with any questions.

Best regards,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Educational without being condescending",
            "Includes required risk disclaimers",
            "Uses 'may' and 'potential' appropriately",
            "No guaranteed outcomes promised",
            "Balanced presentation of benefits and limitations",
            "Appropriate length for long setting",
        ],
    },

    # =========================================================================
    # 3. FOLLOW-UP - Friendly, Short (Single-turn)
    # =========================================================================
    {
        "id": "TC003",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.SHORT,
        "scenario": "Following up after a portfolio review meeting",
        "tags": ["follow-up", "portfolio review", "meeting", "check-in", "questions"],
        "conversation": [
            {
                "role": "user",
                "content": "Follow up after a portfolio review meeting last week",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Following Up on Our Portfolio Review",
                "email_body": """Hi [Recipient Name],

I hope you're doing well! I wanted to follow up on our portfolio review from last week and see if any questions have come up since we spoke.

If you'd like to discuss anything further, I'm happy to chat. Just let me know what works for you.

Warm regards,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Brief and to the point",
            "Friendly without being unprofessional",
            "Clear call to action",
            "No pressure tactics",
            "Appropriate length for short setting",
        ],
    },

    # =========================================================================
    # 4. SCHEDULING - Formal, Short (Single-turn)
    # =========================================================================
    {
        "id": "TC004",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.FORMAL,
        "length": LengthEnum.SHORT,
        "scenario": "Scheduling an annual portfolio review meeting",
        "tags": ["scheduling", "annual review", "meeting request", "portfolio review", "appointment"],
        "conversation": [
            {
                "role": "user",
                "content": "Schedule annual review meeting with client",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Scheduling Your Annual Portfolio Review",
                "email_body": """Dear [Recipient Name],

I am writing to schedule your annual portfolio review. This meeting provides an opportunity to assess your current holdings, discuss any changes in your financial situation, and ensure your investment strategy remains aligned with your goals.

Please let me know your availability over the coming weeks, and I will arrange a time that works best for you.

Sincerely,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Formal tone maintained throughout",
            "Clear purpose stated",
            "No urgency or pressure",
            "Professional structure",
            "Appropriate length for short setting",
        ],
    },

    # =========================================================================
    # 5. FEEDBACK REQUEST - Casual, Medium (Single-turn)
    # =========================================================================
    {
        "id": "TC005",
        "purpose": PurposeEnum.FEEDBACK_REQUEST,
        "tone": ToneEnum.CASUAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Requesting feedback on new client portal experience",
        "tags": ["feedback", "client portal", "user experience", "survey", "improvement"],
        "conversation": [
            {
                "role": "user",
                "content": "Ask for feedback on the new client portal experience",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Quick Question About the New Client Portal",
                "email_body": """Hey [Recipient Name],

I hope you've had a chance to explore our new client portal! I'm reaching out because your feedback would be really valuable as we work to make it as useful as possible.

A few things I'd love to hear your thoughts on:
- How easy was it to navigate and find what you needed?
- Are there any features you'd like to see added?
- Did you run into any issues or confusing areas?

No rush on this—whenever you have a moment, I'd appreciate hearing what you think. Your input helps us improve the experience for everyone.

Thanks!
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Casual but still respectful",
            "Specific questions make feedback easier",
            "No pressure or urgency",
            "Appreciative tone",
            "Appropriate length for medium setting",
        ],
    },

    # =========================================================================
    # 6. EDUCATIONAL CONTENT - Friendly, Medium (Cryptocurrency - High Risk)
    # =========================================================================
    {
        "id": "TC006",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "Client asking about adding cryptocurrency to portfolio",
        "tags": ["cryptocurrency", "crypto", "bitcoin", "volatile", "high risk", "digital assets", "portfolio allocation"],
        "conversation": [
            {
                "role": "user",
                "content": "Client asked about adding cryptocurrency to their portfolio",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Your Question About Cryptocurrency Investments",
                "email_body": """Hi [Recipient Name],

Thanks for reaching out about cryptocurrency! I appreciate you thinking through your investment options carefully.

Cryptocurrency is a highly volatile asset class. Prices can fluctuate dramatically—sometimes 20-30% or more in a single day. You could lose some or all of your invested capital. This level of volatility means crypto may not be suitable for investors with low risk tolerance or short time horizons.

That said, some investors choose to allocate a small portion of their portfolio to digital assets as part of a diversified strategy. The key considerations include your overall risk tolerance, investment timeline, and how a potential loss would impact your financial goals.

I'd recommend we schedule a conversation to discuss whether cryptocurrency aligns with your specific situation. There's no pressure to make any decisions—this is about making sure you have the information you need.

Let me know when works for you!

Best,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Required volatility disclosure included",
            "Clear risk warnings",
            "No promises or predictions about crypto performance",
            "Balanced approach—not dismissive or promotional",
            "Recommends further discussion for suitability",
        ],
    },

    # =========================================================================
    # 7. RELATIONSHIP BUILDER - Formal, Long (New HNW Client Welcome)
    # =========================================================================
    {
        "id": "TC007",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.FORMAL,
        "length": LengthEnum.LONG,
        "scenario": "Welcome letter to new high-net-worth client after account transfer",
        "tags": ["welcome", "new client", "high-net-worth", "HNW", "onboarding", "account transfer", "introduction"],
        "conversation": [
            {
                "role": "user",
                "content": "Welcome letter to a new high-net-worth client who just transferred their accounts",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Welcome to [Company Name] — Your Partnership Begins",
                "email_body": """Dear [Recipient Name],

On behalf of [Company Name], I am pleased to welcome you as a client. We are honored that you have chosen to entrust us with your financial affairs, and I want to personally assure you of our commitment to providing exceptional service.

As your financial advisor, my primary responsibility is to understand your unique circumstances, goals, and concerns. Over the coming weeks, I will work closely with you to develop a comprehensive understanding of your financial picture. This includes reviewing your current holdings, discussing your short-term and long-term objectives, and ensuring our approach aligns with your risk tolerance.

I believe in transparent communication and want you to know exactly what to expect. You will receive regular portfolio statements and performance reports. All fees and costs will be clearly disclosed, and complete information is available upon request. I encourage you to reach out at any time with questions or concerns—your comfort and confidence in our partnership are paramount.

It is important to note that all investments carry risk, including the potential loss of principal. Past performance does not guarantee future results. Our role is to help you pursue your financial goals while managing risk appropriately, not to promise specific outcomes.

I look forward to our initial planning meeting, which we will schedule at your convenience. Please do not hesitate to contact me or my team if you need anything in the meantime.

Thank you again for your trust.

Respectfully,
[Your Name]
[Title]
[Company Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Formal tone appropriate for high-net-worth client",
            "Sets clear expectations",
            "Includes required risk and fee disclosures",
            "No performance promises",
            "Comprehensive yet warm",
            "Appropriate length for long setting",
        ],
    },

    # =========================================================================
    # 8. FOLLOW-UP - Professional, Medium (After Market Decline)
    # =========================================================================
    {
        "id": "TC008",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Checking in with clients after significant market decline",
        "tags": ["market decline", "volatility", "check-in", "reassurance", "market downturn", "client concern"],
        "conversation": [
            {
                "role": "user",
                "content": "Check in with clients after significant market decline this week",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Checking In During Recent Market Volatility",
                "email_body": """Hi [Recipient Name],

Given the market movements we've seen this week, I wanted to reach out and see how you're feeling about your portfolio.

Market volatility, while unsettling, is a normal part of investing. It's natural to feel concerned when you see account values decline. However, I want to remind you that your investment strategy was designed with your long-term goals and risk tolerance in mind.

That said, if your circumstances have changed or if you'd like to discuss your current allocation, I'm here to help. Sometimes these moments prompt valuable conversations about whether our approach still fits your needs.

There's no action required on your part unless you'd like to talk. I simply wanted you to know I'm thinking of you and am available if you have questions or concerns.

Best regards,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Acknowledges concern without panic",
            "No predictions about market recovery",
            "Reassuring without making promises",
            "Offers support without pressure",
            "Appropriately balanced messaging",
        ],
    },

    # =========================================================================
    # 9. SCHEDULING - Friendly, Medium (Retirement Planning for 60th)
    # =========================================================================
    {
        "id": "TC009",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "Scheduling retirement planning discussion for client turning 60",
        "tags": ["retirement", "60th birthday", "milestone", "retirement planning", "social security", "medicare", "scheduling"],
        "conversation": [
            {
                "role": "user",
                "content": "Schedule retirement planning discussion with client turning 60 next year",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Let's Talk About Your Retirement Roadmap",
                "email_body": """Hi [Recipient Name],

With your 60th birthday coming up next year, I thought this would be a great time to schedule a retirement planning conversation. This milestone often prompts important questions about timing, income strategies, and lifestyle goals.

During our meeting, we can discuss:
- Your current retirement timeline and any flexibility you have
- Social Security claiming strategies and their trade-offs
- Income planning for your retirement years
- Healthcare considerations before Medicare eligibility

There's no pressure to make any decisions—this is about making sure you have the information you need to plan confidently. Everyone's situation is different, and what works for one person may not be right for another.

Let me know what times work for you over the next few weeks, and I'll get something scheduled.

Looking forward to connecting!

Best,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Friendly and encouraging",
            "Specific topics create clear value",
            "No urgency or pressure tactics",
            "Acknowledges individual circumstances",
            "Clear call to action",
        ],
    },

    # =========================================================================
    # 10. OTHER - Professional, Short (Compliance Notice - Form CRS)
    # =========================================================================
    {
        "id": "TC010",
        "purpose": PurposeEnum.OTHER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.SHORT,
        "scenario": "Informing clients about updated Form CRS availability",
        "tags": ["compliance", "Form CRS", "regulatory", "disclosure", "required notice"],
        "conversation": [
            {
                "role": "user",
                "content": "Inform clients about updated Form CRS availability",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Updated Form CRS Now Available",
                "email_body": """Hi [Recipient Name],

I wanted to let you know that our updated Form CRS (Client Relationship Summary) is now available. This document provides important information about our services, fees, conflicts of interest, and disciplinary history.

You can access the form on our website at [Website URL] or request a copy by replying to this email.

Please don't hesitate to reach out if you have any questions.

Best regards,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Clear and direct",
            "Provides required regulatory notice",
            "Easy access options given",
            "No unnecessary content",
            "Appropriate length for short setting",
        ],
    },

    # =========================================================================
    # 11. FEEDBACK REQUEST - Formal, Long (Annual Service Review)
    # =========================================================================
    {
        "id": "TC011",
        "purpose": PurposeEnum.FEEDBACK_REQUEST,
        "tone": ToneEnum.FORMAL,
        "length": LengthEnum.LONG,
        "scenario": "Requesting formal feedback on advisory services for annual review",
        "tags": ["feedback", "annual review", "service quality", "client satisfaction", "formal survey"],
        "conversation": [
            {
                "role": "user",
                "content": "Request formal feedback from client about advisory services for annual review",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Request for Your Feedback on Our Advisory Services",
                "email_body": """Dear [Recipient Name],

As part of our commitment to providing exceptional service, I am writing to request your feedback regarding your experience with our advisory services over the past year.

Your perspective is invaluable in helping us understand what we are doing well and where we might improve. I would be grateful if you could take a few moments to share your thoughts on the following areas:

Communication: How satisfied are you with the frequency and quality of our communications? Do you feel adequately informed about your portfolio and relevant market developments?

Responsiveness: When you have reached out with questions or concerns, how would you rate our response time and the helpfulness of our replies?

Service Quality: Are your financial goals being addressed appropriately? Do you feel your investment strategy aligns with your risk tolerance and objectives?

Overall Experience: What aspects of our service have you found most valuable? Are there areas where you believe we could better serve your needs?

Please understand that your honest feedback, whether positive or constructive, is welcomed and appreciated. There is no obligation to respond, but any insights you choose to share will be carefully considered.

You may reply directly to this email or, if you prefer, we can schedule a brief call to discuss your thoughts.

Thank you for your continued trust in our services.

Respectfully,
[Your Name]
[Title]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Formal tone maintained throughout",
            "Specific feedback areas make response easier",
            "No pressure or obligation stated",
            "Offers multiple response options",
            "Professional and appreciative",
        ],
    },

    # =========================================================================
    # 12. EDUCATIONAL CONTENT - Casual, Short (Tax-Loss Harvesting Tip)
    # =========================================================================
    {
        "id": "TC012",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.CASUAL,
        "length": LengthEnum.SHORT,
        "scenario": "Quick reminder about tax-loss harvesting before year end",
        "tags": ["tax-loss harvesting", "year-end", "tax planning", "quick tip", "taxes"],
        "conversation": [
            {
                "role": "user",
                "content": "Quick reminder about tax-loss harvesting before year end",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Quick Year-End Tax Tip",
                "email_body": """Hey [Recipient Name],

Just a quick heads up—year end is approaching, and it might be a good time to review your portfolio for tax-loss harvesting opportunities.

This strategy involves selling investments at a loss to offset gains elsewhere. It's not right for everyone, but worth a conversation if you're interested.

Give me a shout if you'd like to chat about it!

Thanks,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Casual and approachable",
            "Brief educational content",
            "No guarantees or specific tax advice",
            "Acknowledges individual suitability",
            "Clear but no-pressure call to action",
        ],
    },

    # =========================================================================
    # 13. RELATIONSHIP BUILDER - Casual, Short (Birthday Wish)
    # =========================================================================
    {
        "id": "TC013",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.CASUAL,
        "length": LengthEnum.SHORT,
        "scenario": "Sending birthday wishes to long-term client",
        "tags": ["birthday", "celebration", "personal", "relationship", "warm wishes"],
        "conversation": [
            {
                "role": "user",
                "content": "Send birthday wishes to a long-term client",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Happy Birthday!",
                "email_body": """Hey [Recipient Name],

Just wanted to drop a quick note to wish you a very happy birthday! I hope you have a fantastic day celebrating with family and friends.

Cheers to another great year ahead!

Best,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Warm and genuine",
            "Appropriately casual",
            "No business content—purely relationship focused",
            "Short and sweet",
            "Personal touch without overstepping",
        ],
    },

    # =========================================================================
    # 14. OTHER - Casual, Medium (Holiday Office Closure Notice)
    # =========================================================================
    {
        "id": "TC014",
        "purpose": PurposeEnum.OTHER,
        "tone": ToneEnum.CASUAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Notifying clients about holiday office closure and emergency contacts",
        "tags": ["holiday", "office closure", "out of office", "emergency contact", "holiday hours"],
        "conversation": [
            {
                "role": "user",
                "content": "Let clients know about holiday office closure and emergency contact info",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Holiday Hours and How to Reach Us",
                "email_body": """Hey [Recipient Name],

With the holidays coming up, I wanted to give you a quick heads up about our office schedule and how to reach us if needed.

We'll be closed from [Start Date] through [End Date] for the holiday break. During this time, emails and voicemails will be checked periodically, but response times may be slower than usual.

For urgent matters, you can reach our emergency line at [Phone Number]. Please note this is for time-sensitive issues only—routine questions can wait until we're back.

I hope you have a wonderful holiday season! Looking forward to connecting in the new year.

Take care,
[Your Name]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Casual but informative",
            "Clear dates and contact information",
            "Sets appropriate expectations",
            "Warm holiday message",
            "Practical without being overly formal",
        ],
    },

    # =========================================================================
    # 15. SCHEDULING - Professional, Long (Comprehensive Financial Review)
    # =========================================================================
    {
        "id": "TC015",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.LONG,
        "scenario": "Scheduling comprehensive review for client with complex needs",
        "tags": ["comprehensive review", "complex needs", "multiple accounts", "tax planning", "estate planning", "insurance"],
        "conversation": [
            {
                "role": "user",
                "content": "Schedule comprehensive financial review for client with multiple accounts and complex needs",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Scheduling Your Comprehensive Financial Review",
                "email_body": """Hi [Recipient Name],

I hope this message finds you well. Given the complexity of your financial situation and the various accounts we manage together, I would like to schedule a comprehensive financial review at your earliest convenience.

This in-depth review will allow us to examine several important areas of your financial life:

Investment Portfolio Analysis: We will review the performance and allocation of your taxable accounts, retirement accounts, and any other investment vehicles. This includes assessing whether your current strategy remains aligned with your goals and risk tolerance.

Tax Planning Considerations: With multiple account types, there may be opportunities to optimize your tax situation through strategic withdrawals, Roth conversions, or other planning techniques. We can discuss what might make sense for your circumstances.

Estate and Legacy Planning: We should review beneficiary designations across all accounts to ensure they reflect your current wishes. If there have been any life changes, this is an important area to address.

Insurance and Risk Management: A comprehensive review also includes examining your current insurance coverage to identify any potential gaps in protection.

Please note that this meeting typically requires 60-90 minutes to cover these topics thoroughly. I want to ensure we have adequate time to address your questions and concerns without feeling rushed.

To prepare for our meeting, it would be helpful if you could gather any recent statements from accounts held elsewhere and note any questions or changes in your financial situation.

Please let me know your availability over the next two to three weeks, and I will coordinate with my calendar to find a suitable time.

Best regards,
[Your Name]
[Title]""",
                "message_type": "email_generation",
            },
        ],
        "evaluation_notes": [
            "Professional and thorough",
            "Clear agenda sets expectations",
            "No promises about outcomes",
            "Preparation instructions provided",
            "Appropriate length for complex scheduling",
            "Respects client's time",
        ],
    },

    # =========================================================================
    # 16. MULTI-TURN: Refinement - Make Email Shorter
    # =========================================================================
    {
        "id": "TC016",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "User requests shorter version of educational email about bonds",
        "tags": ["refinement", "shorter", "concise", "bonds", "fixed income", "educational"],
        "conversation": [
            {
                "role": "user",
                "content": "Explain how bonds work to a client who is new to investing",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Understanding Bonds: A Foundation for Your Portfolio",
                "email_body": """Hi [Recipient Name],

Thank you for your interest in learning more about bonds. As you build your investment knowledge, understanding fixed income is an important foundation.

A bond is essentially a loan you make to a government or corporation. In return, the issuer promises to pay you interest (called the coupon) at regular intervals and return your principal when the bond matures. For example, a 10-year Treasury bond pays interest twice a year and returns your original investment after 10 years.

Bonds are generally considered less volatile than stocks, which is why many investors include them in their portfolios for stability. However, bonds do carry risks. Interest rate risk means bond prices fall when rates rise. Credit risk refers to the possibility that the issuer cannot make payments. And inflation risk means your fixed payments may lose purchasing power over time.

The role bonds play in your portfolio depends on your goals, timeline, and risk tolerance. For some investors, bonds provide steady income. For others, they serve as a buffer against stock market volatility.

I would be happy to discuss how bonds might fit into your overall investment strategy. Please let me know if you would like to schedule a conversation.

Best regards,
[Your Name]""",
                "message_type": "email_generation",
            },
            {
                "role": "user",
                "content": "This is too long. Can you make it shorter and more digestible?",
                "message_type": "refinement_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Understanding Bonds: The Basics",
                "email_body": """Hi [Recipient Name],

Thanks for asking about bonds! Here's a quick overview.

A bond is a loan you make to a government or company. They pay you interest regularly and return your money when the bond matures. Think of it as an IOU with scheduled payments.

Bonds are generally more stable than stocks, but they're not risk-free. Bond prices fall when interest rates rise, and there's always a small chance the issuer can't pay you back.

Many investors use bonds for steady income or to balance out stock market ups and downs. Whether they're right for you depends on your goals and timeline.

Happy to chat more about this whenever you're ready!

Best,
[Your Name]""",
                "message_type": "email_refinement",
            },
        ],
        "evaluation_notes": [
            "Refinement significantly reduced length while keeping key points",
            "Maintained professional yet accessible tone",
            "Kept essential risk disclosures",
            "Used simpler language in refined version",
            "Preserved call to action",
        ],
    },

    # =========================================================================
    # 17. MULTI-TURN: Refinement - Change Tone from Formal to Friendly
    # =========================================================================
    {
        "id": "TC017",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "User requests more friendly tone for follow-up email",
        "tags": ["refinement", "tone change", "formal to friendly", "follow-up", "meeting"],
        "conversation": [
            {
                "role": "user",
                "content": "Follow up with client after our quarterly meeting",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Follow-Up: Quarterly Portfolio Review",
                "email_body": """Dear [Recipient Name],

I am writing to follow up on our quarterly portfolio review meeting held on [Date]. I wanted to ensure that all your questions were addressed and to reiterate the key points we discussed.

During our meeting, we reviewed your current asset allocation and confirmed it remains aligned with your stated objectives. We also discussed potential adjustments to consider as market conditions evolve.

Should any additional questions arise, please do not hesitate to contact me. I am available at your convenience to discuss any concerns.

Thank you for your continued partnership.

Sincerely,
[Your Name]""",
                "message_type": "email_generation",
            },
            {
                "role": "user",
                "content": "This sounds too stiff. Can you make it more friendly and warm? This is a client I've known for years.",
                "message_type": "refinement_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Great Catching Up!",
                "email_body": """Hi [Recipient Name],

It was great seeing you at our quarterly catch-up! I always enjoy our conversations—they're one of the highlights of my schedule.

Just wanted to follow up and make sure everything we discussed made sense. Your portfolio is looking solid, and I think the adjustments we talked about will serve you well as things evolve.

If anything comes to mind or you just want to chat, you know where to find me. Always happy to talk!

Take care,
[Your Name]""",
                "message_type": "email_refinement",
            },
        ],
        "evaluation_notes": [
            "Tone successfully shifted from formal to friendly",
            "Maintained professionalism despite casual language",
            "Acknowledged long-standing relationship appropriately",
            "Kept core message intact",
            "Natural, conversational language",
        ],
    },

    # =========================================================================
    # 18. MULTI-TURN: Refinement - Add More Detail
    # =========================================================================
    {
        "id": "TC018",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.LONG,
        "scenario": "User requests more detail about what will be covered in meeting",
        "tags": ["refinement", "more detail", "meeting agenda", "estate planning", "beneficiary"],
        "conversation": [
            {
                "role": "user",
                "content": "Schedule a meeting to discuss estate planning updates",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Scheduling Estate Planning Discussion",
                "email_body": """Hi [Recipient Name],

I would like to schedule a meeting to discuss some important estate planning updates. This is a good time to review your current arrangements and ensure everything is up to date.

Please let me know your availability over the next few weeks.

Best regards,
[Your Name]""",
                "message_type": "email_generation",
            },
            {
                "role": "user",
                "content": "Can you add more detail about what we'll cover? I want them to come prepared.",
                "message_type": "refinement_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Scheduling Your Estate Planning Review",
                "email_body": """Hi [Recipient Name],

I would like to schedule a meeting to review your estate planning arrangements. Given recent changes in tax law and the importance of keeping these documents current, this is a valuable conversation to have.

During our meeting, we can cover several key areas:

Beneficiary Designations: We'll review the beneficiaries listed on your retirement accounts, life insurance policies, and investment accounts. It's important these reflect your current wishes, especially if there have been any family changes.

Power of Attorney and Healthcare Directives: We can discuss whether your current documents still name the people you'd want making decisions on your behalf.

Trust Review: If you have a trust, we should confirm it's properly funded and that new assets have been titled appropriately.

Tax Considerations: Recent legislation has impacted estate and gift tax exemptions. We can discuss whether any planning opportunities exist given your situation.

To prepare, it would be helpful to gather your current will, trust documents, and any beneficiary designation forms you have on file. If you've experienced any major life changes—marriage, divorce, births, or deaths in the family—please note those as well.

This meeting typically takes about an hour. Please let me know what times work for you over the next two to three weeks.

Best regards,
[Your Name]""",
                "message_type": "email_refinement",
            },
        ],
        "evaluation_notes": [
            "Added substantial helpful detail",
            "Included preparation instructions",
            "Covered key estate planning topics",
            "Maintained professional tone throughout",
            "No specific legal advice given",
            "Appropriate length for detailed scheduling",
        ],
    },

    # =========================================================================
    # 19. MULTI-TURN: Refinement - Compliance Fix (User asks for non-compliant change)
    # =========================================================================
    {
        "id": "TC019",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "User requests stronger language but advisor maintains compliance",
        "tags": ["refinement", "compliance", "risk disclosure", "investment returns", "market outlook"],
        "conversation": [
            {
                "role": "user",
                "content": "Send an email about why now might be a good time to invest",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Considering Your Investment Options",
                "email_body": """Hi [Recipient Name],

I wanted to reach out about current market conditions and what they might mean for investors with available capital.

After recent market movements, some investors are considering whether this presents an opportunity to put money to work. Historically, periods of market uncertainty have sometimes been followed by recoveries, though past performance is never a guarantee of future results.

If you have funds you've been thinking about investing, it may be worth having a conversation about your options. Any decision should be based on your personal goals, timeline, and risk tolerance—not on trying to time the market.

There's no pressure to act, but I'm here if you'd like to discuss what makes sense for your situation.

Best,
[Your Name]""",
                "message_type": "email_generation",
            },
            {
                "role": "user",
                "content": "Can you make it sound more confident? Say something like 'this is a great time to invest' or 'markets always recover'",
                "message_type": "refinement_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Considering Your Investment Options",
                "email_body": """Hi [Recipient Name],

I wanted to reach out about current market conditions and what they might mean for your investment strategy.

Many long-term investors view periods of market volatility as potential opportunities. While we can't predict short-term movements, staying invested and maintaining a disciplined approach has historically served patient investors well. That said, markets can and do experience extended downturns, and there are no guarantees of recovery within any specific timeframe.

If you have capital you've been considering putting to work, I believe this is a worthwhile conversation to have—not because of any certainty about market direction, but because having a clear strategy is always valuable.

Your comfort level, goals, and timeline should drive any decisions. I'm here to help you think through what makes sense for your specific situation, with no pressure to act.

Would you like to schedule a time to talk?

Best,
[Your Name]""",
                "message_type": "email_refinement",
            },
        ],
        "evaluation_notes": [
            "Politely declined to add non-compliant language",
            "Made email slightly more confident within compliance bounds",
            "Maintained required risk disclosures",
            "Did not say 'markets always recover' or 'great time to invest'",
            "Balanced optimism with appropriate caveats",
            "Added clear disclaimer about no guarantees",
        ],
    },

    # =========================================================================
    # 20. MULTI-TURN: Multiple Refinements
    # =========================================================================
    {
        "id": "TC020",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Multiple rounds of refinement to get email just right",
        "tags": ["refinement", "multiple rounds", "condolences", "life event", "sensitive"],
        "conversation": [
            {
                "role": "user",
                "content": "Send condolences to a client who recently lost their spouse",
                "message_type": "initial_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Thinking of You",
                "email_body": """Dear [Recipient Name],

I was deeply saddened to learn of [Spouse's Name]'s passing. Please accept my heartfelt condolences during this incredibly difficult time.

[Spouse's Name] was a wonderful person, and I know how much they meant to you. The love you shared was evident in every conversation we had together.

Please know that there is no rush to think about financial matters right now. When you're ready—whether that's weeks or months from now—I'll be here to help you navigate any changes that need to be made. Your well-being is the priority.

If there's anything I can do to support you during this time, please don't hesitate to reach out.

With deepest sympathy,
[Your Name]""",
                "message_type": "email_generation",
            },
            {
                "role": "user",
                "content": "I didn't know the spouse personally, can you adjust that part?",
                "message_type": "refinement_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Thinking of You",
                "email_body": """Dear [Recipient Name],

I was deeply saddened to learn of your spouse's passing. Please accept my heartfelt condolences during this incredibly difficult time.

Losing a life partner is one of the most profound losses a person can experience. My thoughts are with you and your family as you navigate this period of grief.

Please know that there is no rush to think about financial matters right now. When you're ready—whether that's weeks or months from now—I'll be here to help you navigate any changes that need to be made. Your well-being is the priority.

If there's anything I can do to support you during this time, please don't hesitate to reach out.

With deepest sympathy,
[Your Name]""",
                "message_type": "email_refinement",
            },
            {
                "role": "user",
                "content": "Good, but can you remove 'incredibly' - it sounds a bit much",
                "message_type": "refinement_request",
            },
            {
                "role": "assistant",
                "content": None,
                "email_subject": "Thinking of You",
                "email_body": """Dear [Recipient Name],

I was deeply saddened to learn of your spouse's passing. Please accept my heartfelt condolences during this difficult time.

Losing a life partner is one of the most profound losses a person can experience. My thoughts are with you and your family as you navigate this period of grief.

Please know that there is no rush to think about financial matters right now. When you're ready—whether that's weeks or months from now—I'll be here to help you navigate any changes that need to be made. Your well-being is the priority.

If there's anything I can do to support you during this time, please don't hesitate to reach out.

With deepest sympathy,
[Your Name]""",
                "message_type": "email_refinement",
            },
        ],
        "evaluation_notes": [
            "Handled sensitive topic with appropriate care",
            "Made incremental refinements without losing meaning",
            "Removed personal claims when advisor didn't know spouse",
            "Respected client's preference for less dramatic language",
            "Maintained sincere and supportive tone throughout",
            "Appropriately de-prioritized financial matters",
        ],
    },
]


# =============================================================================
# RETRIEVAL HELPER FUNCTIONS
# =============================================================================

def get_conversation_by_id(conversation_id: str) -> dict | None:
    """Retrieve a specific conversation by ID."""
    for conv in IDEAL_CONVERSATIONS:
        if conv["id"] == conversation_id:
            return conv
    return None


def get_conversations_by_purpose(purpose: PurposeEnum) -> list[dict]:
    """Retrieve all conversations for a specific purpose."""
    return [conv for conv in IDEAL_CONVERSATIONS if conv["purpose"] == purpose]


def get_conversations_by_tone(tone: ToneEnum) -> list[dict]:
    """Retrieve all conversations for a specific tone."""
    return [conv for conv in IDEAL_CONVERSATIONS if conv["tone"] == tone]


def get_conversations_by_length(length: LengthEnum) -> list[dict]:
    """Retrieve all conversations for a specific length."""
    return [conv for conv in IDEAL_CONVERSATIONS if conv["length"] == length]


def get_multi_turn_conversations() -> list[dict]:
    """Retrieve all conversations that have multiple turns (refinements)."""
    return [conv for conv in IDEAL_CONVERSATIONS if len(conv["conversation"]) > 2]


def get_single_turn_conversations() -> list[dict]:
    """Retrieve all conversations that are single turn (request -> email)."""
    return [conv for conv in IDEAL_CONVERSATIONS if len(conv["conversation"]) == 2]


def get_all_conversations() -> list[dict]:
    """Retrieve all ideal conversations."""
    return IDEAL_CONVERSATIONS


def search_conversations_by_tags(search_tags: list[str], match_all: bool = False) -> list[dict]:
    """
    Search conversations by tags.

    Args:
        search_tags: List of tags to search for
        match_all: If True, conversation must have ALL tags. If False, ANY tag matches.

    Returns:
        List of matching conversations, sorted by number of matching tags (descending)
    """
    results = []
    search_tags_lower = [tag.lower() for tag in search_tags]

    for conv in IDEAL_CONVERSATIONS:
        conv_tags_lower = [tag.lower() for tag in conv.get("tags", [])]
        matching_tags = [tag for tag in search_tags_lower if tag in conv_tags_lower]

        if match_all:
            if len(matching_tags) == len(search_tags_lower):
                results.append((conv, len(matching_tags)))
        else:
            if len(matching_tags) > 0:
                results.append((conv, len(matching_tags)))

    # Sort by number of matching tags (descending)
    results.sort(key=lambda x: x[1], reverse=True)
    return [conv for conv, _ in results]


def find_similar_conversations(
    purpose: PurposeEnum,
    tone: ToneEnum,
    length: LengthEnum,
    user_input: str,
    max_results: int = 3,
) -> list[dict]:
    """
    Find the most relevant conversations based on purpose, tone, length, and input text.

    This is a simple keyword-based retrieval. For production, consider:
    - Embedding-based similarity search
    - Vector database (Pinecone, Weaviate, etc.)

    Args:
        purpose: Email purpose
        tone: Requested tone
        length: Requested length
        user_input: The user's request text
        max_results: Maximum number of conversations to return

    Returns:
        List of most relevant conversations, ranked by relevance
    """
    scored_conversations = []

    # Extract keywords from user input (simple approach)
    user_words = set(user_input.lower().split())

    for conv in IDEAL_CONVERSATIONS:
        score = 0

        # Exact purpose match is most important
        if conv["purpose"] == purpose:
            score += 10

        # Tone match
        if conv["tone"] == tone:
            score += 5

        # Length match
        if conv["length"] == length:
            score += 3

        # Tag matching (keyword overlap)
        conv_tags_lower = [tag.lower() for tag in conv.get("tags", [])]
        for word in user_words:
            if len(word) > 3:  # Skip short words
                for tag in conv_tags_lower:
                    if word in tag or tag in word:
                        score += 2

        # Scenario text matching
        scenario_words = set(conv.get("scenario", "").lower().split())
        overlap = user_words.intersection(scenario_words)
        score += len(overlap) * 1.5

        # Check first user message for similarity
        if conv["conversation"]:
            first_msg = conv["conversation"][0].get("content", "").lower()
            first_msg_words = set(first_msg.split())
            msg_overlap = user_words.intersection(first_msg_words)
            score += len(msg_overlap) * 2

        if score > 0:
            scored_conversations.append((conv, score))

    # Sort by score descending
    scored_conversations.sort(key=lambda x: x[1], reverse=True)

    return [conv for conv, _ in scored_conversations[:max_results]]


def get_conversation_for_refinement(
    purpose: PurposeEnum,
    refinement_type: str,
) -> dict | None:
    """
    Find a conversation that demonstrates a specific type of refinement.

    Args:
        purpose: Email purpose (for context relevance)
        refinement_type: Type of refinement - "shorter", "longer", "tone_change",
                        "more_detail", "compliance_fix"

    Returns:
        A relevant multi-turn conversation, or None if not found
    """
    refinement_keywords = {
        "shorter": ["shorter", "concise", "brief"],
        "longer": ["more detail", "longer", "expand"],
        "tone_change": ["tone", "formal", "friendly", "casual", "warm", "stiff"],
        "more_detail": ["more detail", "add more", "expand", "elaborate"],
        "compliance_fix": ["compliance", "risk", "guarantee", "promise"],
    }

    keywords = refinement_keywords.get(refinement_type, [])
    multi_turn = get_multi_turn_conversations()

    for conv in multi_turn:
        # Check if any refinement request contains the keywords
        for msg in conv["conversation"]:
            if msg.get("message_type") == "refinement_request":
                content_lower = msg.get("content", "").lower()
                if any(kw in content_lower for kw in keywords):
                    return conv

    # Fallback: return any multi-turn conversation with matching purpose
    for conv in multi_turn:
        if conv["purpose"] == purpose:
            return conv

    return multi_turn[0] if multi_turn else None


def extract_email_from_conversation(conversation: dict, get_final: bool = True) -> dict | None:
    """
    Extract the email (subject and body) from a conversation.

    Args:
        conversation: The conversation dict
        get_final: If True, get the last email (after refinements). If False, get the first.

    Returns:
        Dict with 'subject' and 'body' keys, or None if no email found
    """
    emails = []
    for msg in conversation.get("conversation", []):
        if msg.get("email_subject") and msg.get("email_body"):
            emails.append({
                "subject": msg["email_subject"],
                "body": msg["email_body"],
            })

    if not emails:
        return None

    return emails[-1] if get_final else emails[0]


def format_conversation_for_prompt(conversation: dict, include_notes: bool = False) -> str:
    """
    Format a conversation for inclusion in an LLM prompt.

    Args:
        conversation: The conversation dict
        include_notes: Whether to include evaluation notes

    Returns:
        Formatted string representation of the conversation
    """
    lines = []
    lines.append(f"=== Example: {conversation['scenario']} ===")
    lines.append(f"Purpose: {conversation['purpose'].value}")
    lines.append(f"Tone: {conversation['tone'].value}")
    lines.append(f"Length: {conversation['length'].value}")
    lines.append("")

    for msg in conversation["conversation"]:
        role = msg["role"].upper()

        if msg.get("email_subject") and msg.get("email_body"):
            lines.append(f"{role}:")
            lines.append(f"Subject: {msg['email_subject']}")
            lines.append("")
            lines.append(msg["email_body"])
        else:
            lines.append(f"{role}: {msg.get('content', '')}")

        lines.append("")

    if include_notes and conversation.get("evaluation_notes"):
        lines.append("What makes this ideal:")
        for note in conversation["evaluation_notes"]:
            lines.append(f"- {note}")

    return "\n".join(lines)


# =============================================================================
# BACKWARDS COMPATIBILITY
# =============================================================================
# These functions maintain compatibility with code expecting the old structure

def get_test_case_by_id(case_id: str) -> dict | None:
    """
    DEPRECATED: Use get_conversation_by_id instead.
    Retrieve a specific test case by ID (backwards compatible).
    """
    return get_conversation_by_id(case_id)


def get_test_cases_by_purpose(purpose: PurposeEnum) -> list[dict]:
    """
    DEPRECATED: Use get_conversations_by_purpose instead.
    Retrieve all test cases for a specific purpose (backwards compatible).
    """
    return get_conversations_by_purpose(purpose)


def get_test_cases_by_tone(tone: ToneEnum) -> list[dict]:
    """
    DEPRECATED: Use get_conversations_by_tone instead.
    Retrieve all test cases for a specific tone (backwards compatible).
    """
    return get_conversations_by_tone(tone)


def get_all_test_cases() -> list[dict]:
    """
    DEPRECATED: Use get_all_conversations instead.
    Retrieve all test cases (backwards compatible).
    """
    return get_all_conversations()


# Alias for backwards compatibility
IDEAL_TEST_CASES = IDEAL_CONVERSATIONS
