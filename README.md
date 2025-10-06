# ADAC Newsletter Template

This repository contains optimized HTML and plain text email templates for the ADAC member newsletter, designed to avoid spam filters while maintaining professional design and accessibility.

## Files

- `newsletter-template.html` - Spam-filter-friendly HTML email template
- `newsletter-template.txt` - Plain text version for better deliverability
- `mails.txt` - Email distribution list

## Email Best Practices Implemented

### Spam Filter Optimization

1. **Clean HTML Structure**
   - Proper DOCTYPE declaration for email clients
   - Table-based layout for maximum compatibility
   - Inline CSS to avoid external dependencies
   - No JavaScript or external resources

2. **Content Guidelines**
   - Balanced text-to-image ratio
   - Professional language without spam trigger words
   - Clear sender identification
   - Proper unsubscribe mechanisms

3. **Technical Optimization**
   - UTF-8 character encoding
   - Viewport meta tag for mobile responsiveness
   - Apple-specific meta tags for iOS mail clients
   - MSO-specific styles for Outlook compatibility

### Accessibility Features

1. **Semantic HTML**
   - Proper heading hierarchy (h1, h2)
   - Role attributes for tables
   - Alt text support for images (when added)
   - High contrast colors for readability

2. **Mobile Responsiveness**
   - Flexible table layout
   - Media queries for mobile optimization
   - Touch-friendly button sizes
   - Readable font sizes on all devices

### Legal Compliance

1. **Required Elements**
   - Clear sender identification
   - Physical mailing address
   - Unsubscribe link in footer
   - Privacy policy link
   - Reason for receiving email

2. **GDPR Compliance**
   - Email preferences management
   - Clear opt-out mechanism
   - Data protection information

## Usage Instructions

### Customization Variables

Replace the following placeholders in the templates:

- `{{EMAIL_ADDRESS}}` - Recipient's email address
- `{{UNSUBSCRIBE_URL}}` - Link to unsubscribe page
- `{{PREFERENCES_URL}}` - Link to email preferences
- `{{PRIVACY_URL}}` - Link to privacy policy
- `[LINK_URL]` - Links to specific content

### Content Customization

1. **Header Section**
   - Update title and subtitle as needed
   - Maintain ADAC branding colors (#005ca9, #ffcc00)

2. **Content Sections**
   - Replace sample content with actual newsletter content
   - Maintain clear section structure
   - Keep paragraphs concise for readability

3. **Footer Information**
   - Verify contact information is current
   - Update copyright year as needed
   - Ensure legal links are functional

### Testing Recommendations

1. **Spam Filter Testing**
   - Test with multiple email providers (Gmail, Outlook, Yahoo)
   - Use email testing tools (Mail Tester, Litmus)
   - Monitor delivery rates and spam scores

2. **Rendering Testing**
   - Test on desktop and mobile devices
   - Verify rendering in major email clients
   - Check accessibility with screen readers

3. **Performance Monitoring**
   - Track open rates and click-through rates
   - Monitor unsubscribe rates
   - Analyze engagement metrics

## Technical Specifications

### HTML Template
- **File size**: ~7.5KB (optimized for fast loading)
- **Compatibility**: Outlook 2007+, Gmail, Apple Mail, Thunderbird
- **Mobile support**: Responsive design with CSS media queries
- **Encoding**: UTF-8

### Plain Text Template
- **File size**: ~1.2KB
- **Format**: Standard text with clear hierarchy
- **Line length**: <80 characters for readability
- **Structure**: Mirrors HTML content structure

## Color Scheme

- **Primary Blue**: #005ca9 (ADAC brand color)
- **Accent Yellow**: #ffcc00 (ADAC secondary color)
- **Text**: #333333 (high contrast)
- **Background**: #ffffff (clean, professional)
- **Footer**: #f8f8f8 (subtle distinction)

## Font Stack

- Primary: Arial, Helvetica, sans-serif
- Fallback ensures compatibility across all email clients
- Web-safe fonts only (no external font loading)

## Support

For questions about implementation or customization, please refer to email marketing best practices or consult with your email service provider for specific platform requirements.