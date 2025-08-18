# PHASE_2_PROMPT.md

## **Comprehensive IMAP Production Testing & Examples Development**

**Context:** You're working with AnyRFC, a Python library that provides RFC-compliant protocol clients using AnyIO structured concurrency. The IMAP client implementation exists but needs comprehensive real-world testing and production-ready examples.

**Your Mission:** Prove that AnyRFC's IMAP client is production-ready by implementing, testing, and demonstrating ALL major email operations against real IMAP servers (Gmail). Create a complete suite of working examples that showcase the library's capabilities.

### **Phase 1: Core Email Operations (2-3 hours)**
1. **Email Reading & Search**: Connect to Gmail, search for emails by subject, extract metadata
2. **Flag Management**: Mark emails as read/unread, verify changes appear in Gmail web interface  
3. **Real-time Monitoring**: Build email watcher that detects new messages within seconds
4. **Draft Creation**: Use IMAP APPEND to create drafts that appear in Gmail's Drafts folder
5. **Attachment Extraction**: Download email attachments as binary BLOBs, save to files

**Critical Requirements:**
- Test against REAL Gmail account (not mock servers)
- Verify all operations work in Gmail web interface
- Handle IMAP literal continuation protocol correctly
- Use proper byte counts (not character counts) for APPEND operations
- Implement robust connection management for long-running operations

### **Phase 2: Advanced Features (1-2 hours)**
1. **Secret Code Detection**: Build real-time email monitor that extracts specific content patterns
2. **PDF Processing**: Extract PDF attachments and parse text content using PyPDF2
3. **Multi-format Attachments**: Handle various file types (images, documents, archives)
4. **Error Recovery**: Implement robust error handling for network issues and IMAP quirks

### **Phase 3: Production Examples (1-2 hours)**
1. **Clean Architecture**: Create 6-8 professional example scripts with proper documentation
2. **Command-line Arguments**: Make examples configurable via CLI parameters
3. **Environment Variables**: Support multiple IMAP servers (not just Gmail)
4. **Code Organization**: Remove debugging files, create clean README with setup instructions
5. **Dependency Management**: Move optional dependencies (PyPDF2) to examples group

### **Phase 4: Documentation & Insights (30 minutes)**
1. **Update CLAUDE.md**: Document production-ready capabilities with code examples
2. **Record Critical Fixes**: Document IMAP literal continuation solutions
3. **Performance Notes**: Real-time monitoring strategies and Gmail rate limits
4. **Best Practices**: Connection management, error handling, authentication

### **Success Criteria:**
- [ ] Email marked as read in live Gmail shows immediately in web interface
- [ ] Draft email created via IMAP appears in Gmail Drafts folder
- [ ] Real-time monitoring detects new emails within 5 seconds
- [ ] PDF attachment extracted as working file that can be opened
- [ ] All examples work with environment variables (no hardcoded credentials)
- [ ] Clean examples directory with comprehensive documentation
- [ ] CLAUDE.md updated with production-ready implementation notes

### **Constraints:**
- **AnyIO-only**: No asyncio imports, use structured concurrency throughout
- **Real servers**: Test against actual Gmail IMAP, not simulators
- **RFC compliance**: Maintain proper IMAP protocol implementation
- **Production quality**: Code should be ready for real-world usage
- **Clean dependencies**: Keep core library lightweight, optional features in groups

### **Expected Deliverables:**
1. Working email operations suite (read, write, monitor, extract)
2. Clean examples directory with 6-8 documented scripts
3. Comprehensive README with setup and usage instructions
4. Updated CLAUDE.md with production insights and critical fixes
5. Proof that AnyRFC IMAP is production-ready for real email automation

---

**Note:** This prompt encapsulates the comprehensive IMAP development and testing work completed in our session. It represents a complete validation of AnyRFC's email capabilities against real-world servers and the creation of production-ready examples and documentation.