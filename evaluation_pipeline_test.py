"""
Evaluation Pipeline Test Suite
Tests the LLM-based evaluation service with 50 diverse test cases.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.email import PurposeEnum, ToneEnum, LengthEnum
from app.evaluation.evaluation_service import get_evaluation_service
from app.evaluation.test_cases import IDEAL_CONVERSATIONS, extract_email_from_conversation


# =============================================================================
# ADDITIONAL TEST CASES (30 more to reach 50 total)
# =============================================================================

ADDITIONAL_TEST_CASES = [
    # TC021: Educational - Roth IRA Conversion
    {
        "id": "TC021",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Explaining Roth IRA conversion benefits",
        "request": "Explain Roth IRA conversion benefits to a client",
        "email_subject": "Understanding Roth IRA Conversions",
        "email_body": """Hi [Recipient Name],

I wanted to share some information about Roth IRA conversions that may be relevant to your financial planning.

A Roth conversion involves moving funds from a traditional IRA to a Roth IRA. While you would pay taxes on the converted amount now, qualified withdrawals in retirement would be tax-free.

This strategy may be beneficial in certain situations, such as when you expect to be in a higher tax bracket in retirement or want to reduce required minimum distributions. However, it's important to consider your current tax situation and timeline.

The decision to convert depends on many factors unique to your circumstances. I'd recommend we discuss whether this approach aligns with your goals.

Best regards,
[Your Name]"""
    },

    # TC022: Follow-up - After Life Event
    {
        "id": "TC022",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "Following up after client mentioned new grandchild",
        "request": "Follow up with client who mentioned a new grandchild",
        "email_subject": "Congratulations on Your New Grandchild!",
        "email_body": """Hi [Recipient Name],

Congratulations on becoming a grandparent! That's such wonderful news, and I hope everyone is happy and healthy.

If you'd like, we can chat about college savings options like 529 plans when you're ready. There's no rush—enjoy this special time with your family first!

Looking forward to hearing all about the new addition when we connect.

Warmly,
[Your Name]"""
    },

    # TC023: Scheduling - Beneficiary Review
    {
        "id": "TC023",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.SHORT,
        "scenario": "Scheduling annual beneficiary review",
        "request": "Schedule annual beneficiary designation review",
        "email_subject": "Annual Beneficiary Review",
        "email_body": """Hi [Recipient Name],

It's time for our annual beneficiary designation review. This quick check ensures your accounts reflect your current wishes.

Please let me know your availability for a brief call or meeting in the next few weeks.

Best regards,
[Your Name]"""
    },

    # TC024: Relationship Builder - Referral Thank You
    {
        "id": "TC024",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.SHORT,
        "scenario": "Thanking client for referring a friend",
        "request": "Thank a client for referring their friend",
        "email_subject": "Thank You for Your Referral!",
        "email_body": """Hi [Recipient Name],

Thank you so much for referring [Friend's Name] to me! Your trust means a lot, and I'm honored that you'd recommend my services to someone you care about.

I look forward to helping them with their financial goals.

Thanks again,
[Your Name]"""
    },

    # TC025: Educational - Market Commentary
    {
        "id": "TC025",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.FORMAL,
        "length": LengthEnum.LONG,
        "scenario": "Quarterly market commentary during uncertainty",
        "request": "Send quarterly market commentary during economic uncertainty",
        "email_subject": "Q4 Market Update and Outlook",
        "email_body": """Dear [Recipient Name],

I am writing to share our quarterly market perspective and discuss recent economic developments.

The markets have experienced notable volatility this quarter, driven by inflation concerns, interest rate decisions, and geopolitical factors. While short-term fluctuations can be unsettling, it is important to maintain perspective on your long-term investment objectives.

Historical data suggests that markets have weathered similar periods of uncertainty, though past performance does not guarantee future results. Every economic cycle is different, and there are no certainties regarding market direction.

Your portfolio was constructed with your specific goals and risk tolerance in mind. During periods of volatility, the diversification within your portfolio is designed to help manage risk, though it cannot eliminate it entirely.

Key observations this quarter:
- Interest rates remain a significant factor affecting both equity and fixed income markets
- Corporate earnings have shown mixed results across sectors
- Economic indicators suggest a range of possible outcomes

We recommend maintaining your current investment strategy unless your circumstances have changed. Attempting to time market movements often leads to suboptimal outcomes.

I would welcome the opportunity to discuss any questions or concerns you may have. Please do not hesitate to reach out.

Respectfully,
[Your Name]
[Title]"""
    },

    # TC026: Feedback Request - Service Satisfaction
    {
        "id": "TC026",
        "purpose": PurposeEnum.FEEDBACK_REQUEST,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.SHORT,
        "scenario": "Quick satisfaction check after account setup",
        "request": "Ask for feedback on new account setup experience",
        "email_subject": "How Was Your Account Setup Experience?",
        "email_body": """Hi [Recipient Name],

Now that your account setup is complete, I wanted to check in and see how the process went for you.

Was everything clear and straightforward? Is there anything we could have done better?

Your feedback helps us improve. Thanks for taking a moment to share your thoughts.

Best,
[Your Name]"""
    },

    # TC027: Other - Document Request
    {
        "id": "TC027",
        "purpose": PurposeEnum.OTHER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.SHORT,
        "scenario": "Requesting updated documents for compliance",
        "request": "Request updated ID and address verification documents",
        "email_subject": "Document Update Request",
        "email_body": """Hi [Recipient Name],

As part of our regular account maintenance, we need updated copies of your identification and address verification documents.

Please send a copy of your current driver's license or passport, along with a recent utility bill or bank statement showing your address.

You can reply to this email with attachments or upload through our secure portal. Let me know if you have any questions.

Best regards,
[Your Name]"""
    },

    # TC028: Educational - ESG Investing
    {
        "id": "TC028",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "Explaining ESG investing options",
        "request": "Explain ESG investing to client interested in sustainable options",
        "email_subject": "Exploring Sustainable Investing Options",
        "email_body": """Hi [Recipient Name],

Great question about ESG (Environmental, Social, and Governance) investing! I'm happy to share some information.

ESG investing considers factors beyond traditional financial metrics—like a company's environmental practices, how they treat employees, and corporate governance. Some investors find this aligns with their personal values while still pursuing financial returns.

It's worth noting that ESG funds may have different risk/return characteristics than traditional investments, and there's no guarantee they'll outperform or match broader market returns. Performance varies based on the specific strategy and holdings.

If you'd like to explore how ESG options might fit into your portfolio, I'd be happy to discuss further. We can look at available options and see what makes sense for your situation.

Let me know if you'd like to chat!

Best,
[Your Name]"""
    },

    # TC029: Scheduling - Tax Planning Session
    {
        "id": "TC029",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Scheduling year-end tax planning session",
        "request": "Schedule year-end tax planning meeting before December",
        "email_subject": "Year-End Tax Planning Session",
        "email_body": """Hi [Recipient Name],

With the end of the year approaching, this is an ideal time to review your tax situation and explore any planning opportunities before December 31st.

During our session, we can discuss:
- Tax-loss harvesting opportunities in your portfolio
- Charitable giving strategies, including donor-advised funds
- Retirement contribution optimization
- Required minimum distribution planning if applicable

These discussions are most valuable when there's still time to implement strategies, so I'd suggest meeting in the next few weeks.

Please let me know your availability, and I'll get something scheduled.

Best regards,
[Your Name]"""
    },

    # TC030: Follow-up - After Market Drop
    {
        "id": "TC030",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Proactive check-in during market correction",
        "request": "Check in with client during 10% market correction",
        "email_subject": "Checking In During Market Volatility",
        "email_body": """Hi [Recipient Name],

I wanted to reach out given the recent market pullback and see how you're feeling about things.

Market corrections are a normal part of investing, though they're never comfortable to experience. Your portfolio was designed with your long-term goals and risk tolerance in mind, and volatility like this was anticipated in our planning.

That said, if your circumstances have changed or you'd like to talk through what we're seeing, I'm here. Sometimes it helps just to have a conversation.

No action is required on your part. I simply wanted you to know I'm thinking of you and available if needed.

Best regards,
[Your Name]"""
    },

    # TC031: Relationship Builder - Holiday Greeting
    {
        "id": "TC031",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.CASUAL,
        "length": LengthEnum.SHORT,
        "scenario": "Holiday season greeting",
        "request": "Send holiday greetings to clients",
        "email_subject": "Happy Holidays!",
        "email_body": """Hey [Recipient Name],

Just wanted to drop a quick note to wish you and your family a wonderful holiday season!

Here's to a happy, healthy, and prosperous new year ahead.

Take care,
[Your Name]"""
    },

    # TC032: Educational - Alternative Investments
    {
        "id": "TC032",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.FORMAL,
        "length": LengthEnum.LONG,
        "scenario": "Explaining alternative investments to sophisticated investor",
        "request": "Explain alternative investments like private equity and hedge funds",
        "email_subject": "Overview of Alternative Investment Opportunities",
        "email_body": """Dear [Recipient Name],

Thank you for your interest in alternative investments. I would like to provide an overview of this asset class and its potential role in portfolio construction.

Alternative investments include categories such as private equity, hedge funds, real estate, and commodities. These investments differ from traditional stocks and bonds in several important ways.

Key characteristics to understand:
- Liquidity constraints: Many alternatives have lock-up periods and limited redemption windows
- Higher minimum investments: Often require substantial capital commitments
- Complex fee structures: May include management fees plus performance fees
- Limited transparency: Less regulatory disclosure than public markets
- Potential for higher returns, but also different risk profiles

These investments may provide diversification benefits since they often have lower correlation to traditional markets. However, they come with unique risks including illiquidity risk, manager risk, and leverage risk.

It is important to note that past performance of alternative investments does not guarantee future results. These investments are generally suitable only for investors who meet certain income and net worth requirements and who can tolerate illiquidity and complexity.

I would recommend we schedule a detailed discussion to determine whether alternative investments are appropriate given your specific circumstances, goals, and risk tolerance.

Please let me know if you would like to proceed with a more in-depth conversation.

Respectfully,
[Your Name]
[Title]"""
    },

    # TC033: Feedback Request - Website Experience
    {
        "id": "TC033",
        "purpose": PurposeEnum.FEEDBACK_REQUEST,
        "tone": ToneEnum.CASUAL,
        "length": LengthEnum.SHORT,
        "scenario": "Asking for feedback on new website",
        "request": "Get feedback on our new website",
        "email_subject": "What Do You Think of Our New Website?",
        "email_body": """Hey [Recipient Name],

Have you had a chance to check out our new website yet?

We'd love to know what you think! Is it easy to find what you need? Anything confusing or missing?

Just hit reply and let me know—your feedback really helps!

Thanks,
[Your Name]"""
    },

    # TC034: Scheduling - Insurance Review
    {
        "id": "TC034",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.SHORT,
        "scenario": "Scheduling insurance coverage review",
        "request": "Schedule insurance coverage review meeting",
        "email_subject": "Let's Review Your Insurance Coverage",
        "email_body": """Hi [Recipient Name],

It's been a while since we reviewed your insurance coverage. Life changes, and it's worth making sure your protection keeps up!

Got time for a quick review in the next few weeks? We'll make sure everything still fits your needs.

Let me know what works for you!

Best,
[Your Name]"""
    },

    # TC035: Other - Privacy Policy Update
    {
        "id": "TC035",
        "purpose": PurposeEnum.OTHER,
        "tone": ToneEnum.FORMAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Notifying clients of privacy policy update",
        "request": "Inform clients about updated privacy policy",
        "email_subject": "Important: Updated Privacy Policy",
        "email_body": """Dear [Recipient Name],

I am writing to inform you of updates to our Privacy Policy, effective [Effective Date].

We have revised our privacy practices to enhance the protection of your personal information and to comply with current regulatory requirements. Key changes include:

- Enhanced data encryption standards
- Updated procedures for handling data requests
- Clarified information sharing practices with service providers

You may review the complete updated Privacy Policy on our website at [Website URL]. A copy is also available upon request.

These changes do not require any action on your part. We remain committed to protecting your personal information.

Please contact our office if you have any questions.

Sincerely,
[Your Name]
[Title]"""
    },

    # TC036: Educational - Bond Ladder Strategy
    {
        "id": "TC036",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Explaining bond ladder strategy for income",
        "request": "Explain bond laddering strategy for retirement income",
        "email_subject": "Bond Laddering: A Strategy for Retirement Income",
        "email_body": """Hi [Recipient Name],

I wanted to share information about bond laddering, a strategy that may be worth considering for your retirement income needs.

A bond ladder involves purchasing bonds with staggered maturity dates. For example, you might buy bonds maturing in one, two, three, four, and five years. As each bond matures, you can either use the proceeds for income or reinvest in a new bond at the long end of your ladder.

Potential benefits of this approach include:
- Regular income from coupon payments
- Reduced interest rate risk compared to owning all long-term bonds
- Flexibility to adjust as rates change

However, bond ladders are not without risk. Bond prices fluctuate with interest rates, and there's always credit risk depending on the issuer. Additionally, reinvestment risk exists when bonds mature during low-rate environments.

This strategy works best for investors with specific income needs and appropriate time horizons. I'd be happy to discuss whether it might fit your situation.

Best regards,
[Your Name]"""
    },

    # TC037: Follow-up - After Initial Consultation
    {
        "id": "TC037",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.SHORT,
        "scenario": "Following up after initial consultation with prospect",
        "request": "Follow up with prospect after initial meeting",
        "email_subject": "Great Meeting You!",
        "email_body": """Hi [Recipient Name],

It was great meeting with you yesterday! I enjoyed learning about your goals and answering your questions.

If anything else comes to mind, don't hesitate to reach out. I'm happy to help however I can.

Looking forward to staying in touch!

Best,
[Your Name]"""
    },

    # TC038: Relationship Builder - Work Anniversary
    {
        "id": "TC038",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.SHORT,
        "scenario": "Acknowledging client's work anniversary or promotion",
        "request": "Congratulate client on their promotion",
        "email_subject": "Congratulations on Your Promotion!",
        "email_body": """Hi [Recipient Name],

I just heard about your promotion—congratulations! That's a wonderful recognition of your hard work and dedication.

If this change affects your financial situation (new benefits, deferred compensation, etc.), I'm here to help you make the most of it.

Best wishes on this exciting new chapter!

Regards,
[Your Name]"""
    },

    # TC039: Scheduling - New Client Onboarding
    {
        "id": "TC039",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "Scheduling onboarding meeting with new client",
        "request": "Schedule onboarding meeting for new client",
        "email_subject": "Let's Get Started! Scheduling Your Onboarding",
        "email_body": """Hi [Recipient Name],

Welcome aboard! I'm excited to begin working together and help you pursue your financial goals.

For our first meeting, I'd like to get to know you better—your priorities, concerns, and what success looks like to you. We'll also review the paperwork and answer any questions you have about the process.

The meeting typically takes about an hour. Here are a few things that would be helpful to bring:
- Recent statements from existing investment accounts
- Any relevant tax documents
- A list of questions you'd like to discuss

Let me know what times work for you, and I'll get us scheduled!

Looking forward to it,
[Your Name]"""
    },

    # TC040: Other - Account Transfer Status
    {
        "id": "TC040",
        "purpose": PurposeEnum.OTHER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.SHORT,
        "scenario": "Updating client on account transfer status",
        "request": "Update client on pending account transfer status",
        "email_subject": "Update on Your Account Transfer",
        "email_body": """Hi [Recipient Name],

I wanted to give you a quick update on your account transfer. We've submitted all paperwork and are waiting for [Previous Firm Name] to complete the transfer.

These transfers typically take 5-7 business days. I'll keep you posted and let you know as soon as everything is settled.

Questions in the meantime? Just reach out.

Best regards,
[Your Name]"""
    },

    # TC041: Educational - Required Minimum Distributions
    {
        "id": "TC041",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Explaining RMD requirements to client approaching 73",
        "request": "Explain RMD requirements for client turning 73",
        "email_subject": "Understanding Your Required Minimum Distributions",
        "email_body": """Hi [Recipient Name],

As you approach your 73rd birthday, I wanted to provide some information about Required Minimum Distributions (RMDs) from your retirement accounts.

The IRS requires you to begin taking annual distributions from traditional IRAs and employer-sponsored retirement plans starting the year you turn 73. These distributions are calculated based on your account balance and life expectancy tables.

Key points to understand:
- Your first RMD can be delayed until April 1 of the year after you turn 73, but this means taking two RMDs that year
- RMDs are taxed as ordinary income
- Failing to take your RMD can result in a significant penalty

We should discuss strategies for meeting your RMD requirements while minimizing tax impact. Options may include Qualified Charitable Distributions if you make charitable gifts, or timing strategies across multiple accounts.

I'd recommend we schedule a conversation to review your specific situation before year-end.

Best regards,
[Your Name]"""
    },

    # TC042: Feedback Request - Meeting Experience
    {
        "id": "TC042",
        "purpose": PurposeEnum.FEEDBACK_REQUEST,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.SHORT,
        "scenario": "Requesting feedback after annual review meeting",
        "request": "Get feedback after annual review meeting",
        "email_subject": "How Was Our Annual Review?",
        "email_body": """Hi [Recipient Name],

Thanks again for meeting with me for your annual review!

I'd love to hear your thoughts—did we cover everything you wanted? Anything you wish we had spent more time on?

Your feedback helps me make our meetings as valuable as possible. Just hit reply!

Best,
[Your Name]"""
    },

    # TC043: Follow-up - After Life Insurance Discussion
    {
        "id": "TC043",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Following up on life insurance discussion",
        "request": "Follow up after discussing life insurance needs",
        "email_subject": "Following Up on Our Insurance Discussion",
        "email_body": """Hi [Recipient Name],

Thank you for our conversation about your life insurance needs. I wanted to follow up with some additional thoughts.

Based on what you shared, a term life policy may provide the coverage you need at a reasonable cost. However, whole life or universal life policies might also be worth considering depending on your estate planning goals. Each has different features and costs.

Before making any decisions, I'd recommend we review:
- Your current coverage and any gaps
- Your family's income replacement needs
- How insurance fits into your broader financial plan

I can prepare some illustrations showing different options if you'd like to compare. Just let me know, and I'll put something together.

Best regards,
[Your Name]"""
    },

    # TC044: Relationship Builder - Sympathy Note
    {
        "id": "TC044",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.FORMAL,
        "length": LengthEnum.SHORT,
        "scenario": "Sending sympathy to client who lost a parent",
        "request": "Send condolences to client who lost their mother",
        "email_subject": "With Sympathy",
        "email_body": """Dear [Recipient Name],

I was deeply saddened to learn of your mother's passing. Please accept my sincere condolences during this difficult time.

My thoughts are with you and your family. Please take all the time you need, and know that I am here whenever you are ready to talk.

With deepest sympathy,
[Your Name]"""
    },

    # TC045: Scheduling - Mid-Year Review
    {
        "id": "TC045",
        "purpose": PurposeEnum.SCHEDULING,
        "tone": ToneEnum.CASUAL,
        "length": LengthEnum.SHORT,
        "scenario": "Scheduling mid-year portfolio check-in",
        "request": "Schedule mid-year portfolio review",
        "email_subject": "Mid-Year Check-In?",
        "email_body": """Hey [Recipient Name],

We're halfway through the year already—can you believe it? Time for our mid-year check-in!

Got 30 minutes in the next couple weeks? Let's make sure everything's on track.

Let me know what works!

Thanks,
[Your Name]"""
    },

    # TC046: Educational - Social Security Timing
    {
        "id": "TC046",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.LONG,
        "scenario": "Explaining Social Security claiming strategies",
        "request": "Explain Social Security claiming options for client near retirement",
        "email_subject": "Understanding Your Social Security Options",
        "email_body": """Hi [Recipient Name],

Since you're approaching retirement, I thought it would be helpful to discuss Social Security claiming strategies. When you claim can significantly impact your lifetime benefits.

Here's a quick overview of your options:

Early Claiming (Age 62-66):
You can start benefits as early as 62, but your monthly amount will be permanently reduced. For each year you claim before your Full Retirement Age (FRA), benefits are reduced by approximately 5-7%. This might make sense if you need the income or have health concerns.

Full Retirement Age (66-67):
Claiming at FRA means you receive your full calculated benefit. Your specific FRA depends on your birth year.

Delayed Claiming (Age 67-70):
For each year you delay past FRA, your benefit increases by about 8% until age 70. This can result in a significantly higher monthly payment but means waiting longer to receive benefits.

There's no universally right answer—the best strategy depends on your health, other income sources, whether you're married, and your overall financial plan. Married couples have additional strategies to consider, like spousal benefits and survivor benefits.

Past performance of any claiming strategy does not guarantee results for your situation, as life expectancy and personal circumstances vary greatly.

I'd love to run some projections specific to your situation. Want to schedule a time to go through the numbers together?

Best,
[Your Name]"""
    },

    # TC047: Other - Secure Message Notification
    {
        "id": "TC047",
        "purpose": PurposeEnum.OTHER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.SHORT,
        "scenario": "Notifying client of secure document in portal",
        "request": "Notify client about secure document available in portal",
        "email_subject": "Secure Document Available for Your Review",
        "email_body": """Hi [Recipient Name],

You have a new secure document available in your client portal. Please log in at your convenience to review it.

If you have any questions about the document, feel free to reach out.

Best regards,
[Your Name]"""
    },

    # TC048: Follow-up - Seminar Attendee
    {
        "id": "TC048",
        "purpose": PurposeEnum.FOLLOW_UP,
        "tone": ToneEnum.FRIENDLY,
        "length": LengthEnum.MEDIUM,
        "scenario": "Following up with seminar attendee",
        "request": "Follow up with someone who attended our retirement planning seminar",
        "email_subject": "Thanks for Attending Our Retirement Planning Seminar!",
        "email_body": """Hi [Recipient Name],

Thank you for joining us at our retirement planning seminar last week! I hope you found the information valuable.

A few resources you might find helpful:
- The retirement planning checklist we discussed is attached
- Our website has additional articles on the topics we covered

If you have questions about anything we discussed or would like to explore how these concepts apply to your specific situation, I'd be happy to chat. There's no obligation—just a chance to answer your questions.

Feel free to reach out anytime!

Best,
[Your Name]"""
    },

    # TC049: Relationship Builder - Business Anniversary
    {
        "id": "TC049",
        "purpose": PurposeEnum.RELATIONSHIP_BUILDER,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Celebrating client's business anniversary",
        "request": "Congratulate business owner client on 25 years in business",
        "email_subject": "Congratulations on 25 Years in Business!",
        "email_body": """Hi [Recipient Name],

Congratulations on reaching 25 years in business! That's an incredible milestone that speaks to your hard work, dedication, and resilience.

Building and sustaining a successful business for a quarter century is no small feat. You've navigated countless challenges and created something truly meaningful.

As you look toward the next chapter, whether that's continued growth, succession planning, or eventually transitioning the business, I'm here to help ensure your personal financial goals stay on track.

Here's to the next 25 years!

Best regards,
[Your Name]"""
    },

    # TC050: Educational - Inflation Impact
    {
        "id": "TC050",
        "purpose": PurposeEnum.EDUCATIONAL_CONTENT,
        "tone": ToneEnum.PROFESSIONAL,
        "length": LengthEnum.MEDIUM,
        "scenario": "Explaining inflation impact on retirement planning",
        "request": "Explain how inflation affects retirement savings",
        "email_subject": "Understanding Inflation's Impact on Your Retirement",
        "email_body": """Hi [Recipient Name],

I wanted to share some thoughts on a topic that affects every retirement plan: inflation.

Inflation erodes purchasing power over time. What costs $100 today may cost $150 or more in 15 years. For retirees, this means the income you need in year one of retirement will likely need to grow throughout your retirement years.

This has several implications for planning:
- Your retirement income needs should account for rising costs
- Fixed income sources like pensions and Social Security may not keep pace
- Investment strategies should consider inflation protection

Some strategies that may help include:
- Treasury Inflation-Protected Securities (TIPS)
- Maintaining some equity exposure for growth potential
- Building in spending flexibility for unexpected increases

Of course, there's no way to predict future inflation precisely. Historical averages provide guidance but not guarantees. What matters is building a plan with flexibility to adapt.

I'd be happy to review how inflation assumptions factor into your current retirement projections. Let me know if you'd like to discuss.

Best regards,
[Your Name]"""
    },
]


def run_tests():
    """Run the evaluation test suite."""
    print("=" * 80)
    print("FMG MUSE EVALUATION PIPELINE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # Collect all test cases
    all_test_cases = []

    # Add test cases from IDEAL_CONVERSATIONS (first 20)
    for conv in IDEAL_CONVERSATIONS:
        email = extract_email_from_conversation(conv)
        if email:
            all_test_cases.append({
                "id": conv["id"],
                "purpose": conv["purpose"],
                "tone": conv["tone"],
                "length": conv["length"],
                "scenario": conv["scenario"],
                "request": conv["conversation"][0]["content"] if conv["conversation"] else "",
                "email_subject": email["subject"],
                "email_body": email["body"],
            })

    # Add additional test cases (30 more)
    all_test_cases.extend(ADDITIONAL_TEST_CASES)

    print(f"Total Test Cases: {len(all_test_cases)}")
    print()

    # Run async test
    results = asyncio.run(evaluate_test_cases(all_test_cases))

    # Generate summary
    generate_summary(results)


async def evaluate_test_cases(test_cases: list) -> list:
    """Evaluate all test cases asynchronously."""
    results = []
    eval_service = get_evaluation_service()

    total = len(test_cases)
    passed = 0
    failed = 0
    errors = 0

    for i, tc in enumerate(test_cases):
        print(f"\n[{i+1}/{total}] Testing: {tc['id']} - {tc['scenario'][:50]}...")

        try:
            metrics = await eval_service.evaluate_email(
                email_subject=tc["email_subject"],
                email_body=tc["email_body"],
                purpose=tc["purpose"],
                tone=tc["tone"],
                length=tc["length"],
                original_request=tc["request"],
            )

            result = {
                "id": tc["id"],
                "scenario": tc["scenario"],
                "purpose": tc["purpose"].value,
                "tone": tc["tone"].value,
                "length": tc["length"].value,
                "overall_score": metrics.overall_score,
                "pass_threshold": metrics.pass_threshold,
                "compliance_score": metrics.compliance.score,
                "compliance_justification": metrics.compliance.justification,
                "tone_consistency_score": metrics.tone_consistency.score,
                "length_accuracy_score": metrics.length_accuracy.score,
                "structure_completeness_score": metrics.structure_completeness.score,
                "purpose_alignment_score": metrics.purpose_alignment.score,
                "clarity_score": metrics.clarity.score,
                "professionalism_score": metrics.professionalism.score,
                "personalization_score": metrics.personalization.score,
                "risk_balance_score": metrics.risk_balance.score,
                "disclaimer_accuracy_score": metrics.disclaimer_accuracy.score,
                "strengths": metrics.strengths,
                "improvements_needed": metrics.improvements_needed,
                "rewrite_recommended": metrics.rewrite_recommended,
                "status": "PASS" if metrics.pass_threshold else "FAIL",
                "error": None,
            }

            if metrics.pass_threshold:
                passed += 1
                print(f"    PASS - Score: {metrics.overall_score:.2f} | Compliance: {metrics.compliance.score}/10")
            else:
                failed += 1
                print(f"    FAIL - Score: {metrics.overall_score:.2f} | Compliance: {metrics.compliance.score}/10")
                if metrics.improvements_needed:
                    print(f"    Issues: {', '.join(metrics.improvements_needed[:2])}")

        except Exception as e:
            errors += 1
            result = {
                "id": tc["id"],
                "scenario": tc["scenario"],
                "purpose": tc["purpose"].value,
                "tone": tc["tone"].value,
                "length": tc["length"].value,
                "overall_score": 0,
                "pass_threshold": False,
                "status": "ERROR",
                "error": str(e),
            }
            print(f"    ERROR - {str(e)[:50]}...")

        results.append(result)

    print()
    print("=" * 80)
    print(f"RESULTS: {passed} PASSED | {failed} FAILED | {errors} ERRORS")
    print("=" * 80)

    return results


def generate_summary(results: list):
    """Generate a comprehensive test summary."""
    print()
    print("=" * 80)
    print("DETAILED TEST SUMMARY")
    print("=" * 80)

    # Overall statistics
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    errors = sum(1 for r in results if r.get("status") == "ERROR")

    valid_results = [r for r in results if r.get("status") != "ERROR"]

    if valid_results:
        avg_score = sum(r["overall_score"] for r in valid_results) / len(valid_results)
        avg_compliance = sum(r.get("compliance_score", 0) for r in valid_results) / len(valid_results)
    else:
        avg_score = 0
        avg_compliance = 0

    print()
    print("OVERALL STATISTICS:")
    print("-" * 40)
    print(f"Total Test Cases:     {total}")
    print(f"Passed:               {passed} ({passed/total*100:.1f}%)")
    print(f"Failed:               {failed} ({failed/total*100:.1f}%)")
    print(f"Errors:               {errors} ({errors/total*100:.1f}%)")
    print(f"Average Score:        {avg_score:.2f}/10")
    print(f"Average Compliance:   {avg_compliance:.1f}/10")

    # By purpose
    print()
    print("RESULTS BY PURPOSE:")
    print("-" * 40)
    purposes = {}
    for r in results:
        p = r.get("purpose", "unknown")
        if p not in purposes:
            purposes[p] = {"pass": 0, "fail": 0, "error": 0, "scores": []}
        if r.get("status") == "PASS":
            purposes[p]["pass"] += 1
        elif r.get("status") == "FAIL":
            purposes[p]["fail"] += 1
        else:
            purposes[p]["error"] += 1
        if r.get("overall_score"):
            purposes[p]["scores"].append(r["overall_score"])

    for purpose, stats in sorted(purposes.items()):
        avg = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
        print(f"  {purpose:25s}: {stats['pass']} pass, {stats['fail']} fail, {stats['error']} error (avg: {avg:.2f})")

    # By tone
    print()
    print("RESULTS BY TONE:")
    print("-" * 40)
    tones = {}
    for r in results:
        t = r.get("tone", "unknown")
        if t not in tones:
            tones[t] = {"pass": 0, "fail": 0, "error": 0, "scores": []}
        if r.get("status") == "PASS":
            tones[t]["pass"] += 1
        elif r.get("status") == "FAIL":
            tones[t]["fail"] += 1
        else:
            tones[t]["error"] += 1
        if r.get("overall_score"):
            tones[t]["scores"].append(r["overall_score"])

    for tone, stats in sorted(tones.items()):
        avg = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
        print(f"  {tone:15s}: {stats['pass']} pass, {stats['fail']} fail, {stats['error']} error (avg: {avg:.2f})")

    # By length
    print()
    print("RESULTS BY LENGTH:")
    print("-" * 40)
    lengths = {}
    for r in results:
        l = r.get("length", "unknown")
        if l not in lengths:
            lengths[l] = {"pass": 0, "fail": 0, "error": 0, "scores": []}
        if r.get("status") == "PASS":
            lengths[l]["pass"] += 1
        elif r.get("status") == "FAIL":
            lengths[l]["fail"] += 1
        else:
            lengths[l]["error"] += 1
        if r.get("overall_score"):
            lengths[l]["scores"].append(r["overall_score"])

    for length, stats in sorted(lengths.items()):
        avg = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
        print(f"  {length:10s}: {stats['pass']} pass, {stats['fail']} fail, {stats['error']} error (avg: {avg:.2f})")

    # Metric averages
    if valid_results:
        print()
        print("METRIC AVERAGES (across all valid tests):")
        print("-" * 40)
        metrics = [
            ("compliance_score", "Compliance"),
            ("tone_consistency_score", "Tone Consistency"),
            ("length_accuracy_score", "Length Accuracy"),
            ("structure_completeness_score", "Structure"),
            ("purpose_alignment_score", "Purpose Alignment"),
            ("clarity_score", "Clarity"),
            ("professionalism_score", "Professionalism"),
            ("personalization_score", "Personalization"),
            ("risk_balance_score", "Risk Balance"),
            ("disclaimer_accuracy_score", "Disclaimer Accuracy"),
        ]
        for key, name in metrics:
            scores = [r.get(key, 0) for r in valid_results if r.get(key)]
            if scores:
                avg = sum(scores) / len(scores)
                print(f"  {name:25s}: {avg:.1f}/10")

    # Failed tests details
    failed_tests = [r for r in results if r.get("status") == "FAIL"]
    if failed_tests:
        print()
        print("FAILED TESTS DETAILS:")
        print("-" * 40)
        for r in failed_tests:
            print(f"  {r['id']}: {r['scenario'][:40]}...")
            print(f"    Score: {r['overall_score']:.2f} | Compliance: {r.get('compliance_score', 'N/A')}")
            if r.get("improvements_needed"):
                print(f"    Issues: {', '.join(r['improvements_needed'][:2])}")

    # Error tests
    error_tests = [r for r in results if r.get("status") == "ERROR"]
    if error_tests:
        print()
        print("ERROR TESTS:")
        print("-" * 40)
        for r in error_tests:
            print(f"  {r['id']}: {r.get('error', 'Unknown error')[:60]}...")

    # Save results to JSON
    output_file = f"eval_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "pass_rate": passed/total*100 if total > 0 else 0,
                "average_score": avg_score,
                "average_compliance": avg_compliance,
            },
            "results": results,
        }, f, indent=2)

    print()
    print(f"Full results saved to: {output_file}")
    print()
    print("=" * 80)
    print(f"Test suite completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
