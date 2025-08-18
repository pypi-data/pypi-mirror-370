- ALWAYS run Python things with `uv`

# Production Testing Insights

## Verified Real-World IMAP Operations

During development, we successfully tested all major IMAP operations against live Gmail:

### 🎯 Email Reading & Flag Management
- Successfully searched for and marked emails as read in real Gmail inbox
- Verified flags show up immediately in Gmail web interface
- STORE command works perfectly with Gmail's IMAP implementation

### 📧 Draft Creation (CRITICAL FIXES)
- **MAJOR DISCOVERY**: Gmail requires exact byte counts, not character counts for APPEND
- **Fixed literal continuation**: Must read untagged responses before tagged completion
- **Working solution**: Created drafts that appear in Gmail web interface immediately

### 🕵️ Real-Time Email Monitoring  
- Built working real-time email alerter that detects new emails within 3-5 seconds
- Successfully extracted secret codes from live email content
- Confirmed real-time IMAP polling is viable for production use

### 📎 Attachment Extraction (BLOBS)
- **SUCCESS**: Extracted 178KB PDF attachment as binary BLOB
- Successfully decoded BASE64 → binary and saved working PDF file
- Verified PDF content extraction with PyPDF2 (academic paper about BloomUnit)

## Example Code Quality
- Started with 30+ debugging/testing files
- Cleaned up to 8 production-ready examples with proper documentation
- All examples now accept command-line arguments and environment variables
- Removed all hardcoded personal email addresses and test data

## Dependencies Management
- **CRITICAL**: Moved PyPDF2 from main deps to examples group
- Keeps core library lightweight while supporting rich examples
- Proper use of `uv` dependency groups for optional functionality