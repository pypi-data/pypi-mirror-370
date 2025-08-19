---
title: "Extensions and Customization"
layout: single
permalink: /extensions/
sidebar:
  nav: "docs"
toc: true
toc_label: "Extensions"
toc_icon: "puzzle-piece"
---

This section covers how to extend Insight Ingenious - an enterprise-grade Python library for AI agent APIs - with custom components, advanced configurations, and Azure service integrations. The library's extensive customization capabilities enable tailored solutions for specific enterprise requirements.

## Available Extension Guides

### Core Extensions
- **[Custom Agents](./custom-agents.md)** - Create specialized AI agents for specific tasks
- **[Conversation Patterns](./conversation-patterns.md)** - Design custom multi-agent conversation flows
- **[Flow Implementation](./flow-implementation.md)** - Implement custom workflow logic
- **[Custom Templates](./custom-templates.md)** - Create and modify prompt templates

## Getting Started with Extensions

Before creating custom extensions, ensure you have:

1. **A working Insight Ingenious installation** - See [Getting Started](../getting-started/README.md)
2. **Understanding of core workflows** - See [Workflows](../workflows/README.md)
3. **Development environment setup** - See [Development Guide](../development/README.md)

## Extension Architecture

Insight Ingenious uses a modular architecture that supports both external and internal extensions. The **recommended approach is external extensions** to avoid modifying library code:

### External Extension Structure (Recommended)
```
your_project/
└── ingenious_extensions/
    ├── __init__.py
    ├── services/
    │   └── chat_services/
    │       └── multi_agent/
    │           └── conversation_flows/     # Custom agent workflows
    │               └── your_agent_name/
    │                   ├── __init__.py
    │                   ├── your_agent_name.py
    │                   └── templates/
    │                       └── prompts/
    │                           └── agent_prompt.jinja
    └── models/
        └── agent.py                       # Custom data models
```

### Library Extension Structure (Internal)
```
ingenious/
├── services/
│   └── chat_services/
│       └── multi_agent/
│           ├── agents/           # Internal custom agents
│           ├── conversation_patterns/  # Conversation patterns
│           └── conversation_flows/     # Internal flow implementations
├── templates/
│   └── prompts/                 # Internal prompt templates
└── ingenious_extensions_template/  # Extension template for copying external extensions
```

### Extension Discovery Mechanism

The system uses a 3-tier discovery pattern for maximum flexibility:

1. **`ingenious_extensions`** - Your local external extensions (first priority)
2. **`ingenious.ingenious_extensions_template`** - Library template location (second priority)
3. **`ingenious.services.chat_services.multi_agent.conversation_flows`** - Core library flows (fallback)

This allows you to:
- Develop extensions independently of the library
- Test extensions locally before deployment
- Override library functionality without modification
- Maintain clean separation between custom and core code

## Extension Development Workflow

### External Extension Development (Recommended)

1. **Plan your extension** - Define the specific functionality you want to add
2. **Create external structure** - Set up the `ingenious_extensions` directory structure
3. **Implement IConversationFlow** - Create your agent workflow using the interface pattern
4. **Add template fallbacks** - Ensure your extension works without Azure storage
5. **Test locally** - Test your extension in the `ingenious_extensions` directory
6. **Copy to template location** - Copy to `ingenious_extensions_template` for system discovery
7. **Test via API** - Verify the workflow works through the chat API
8. **Document your extension** - Create clear documentation for others

### Internal Extension Development (Library Modification)

1. **Plan your extension** - Define the specific functionality you want to add
2. **Choose the right extension type** - Agent, pattern, flow, or template
3. **Follow the appropriate guide** - Use the guides in this section
4. **Test your extension** - Ensure it works with existing workflows
5. **Document your extension** - Create clear documentation for others

## Best Practices

### External Extension Best Practices (Recommended)

- **Use external pattern** - Prefer `ingenious_extensions` over modifying library code
- **Implement template fallbacks** - Always provide fallback templates for Azure storage failures
- **Follow IConversationFlow interface** - Use the interface pattern for proper integration
- **Handle errors gracefully** - Wrap workflows in try-catch blocks with meaningful error messages
- **Test discovery mechanism** - Verify your extensions are found via the 3-tier discovery system
- **Keep dependencies minimal** - Only import what's necessary from the library
- **Document deployment** - Include instructions for copying to template locations

### General Extension Best Practices

- **Follow naming conventions** - Use descriptive, lowercase names with underscores
- **Match directory structure** - Flow directories must match the flow name exactly
- **Test thoroughly** - Test your extensions with different inputs and scenarios
- **Handle errors gracefully** - Always provide fallback templates and error handling
- **Document well** - Include clear instructions and examples
- **Keep it modular** - Design extensions to be reusable and maintainable
- **Version control** - Track changes to your custom extensions
- **Test both patterns** - Verify your flows work with both local and Azure storage configurations

## Need Help?

- Check the [Troubleshooting Guide](../getting-started/troubleshooting.md)
- Review existing extensions in the codebase for examples
- Consult the [Development Documentation](../development/README.md)
- Ask questions in the project repository

## Contributing Extensions

If you've created a useful extension, consider contributing it back to the project:

1. Fork the repository
2. Create a feature branch
3. Add your extension with proper documentation
4. Submit a pull request

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed contribution guidelines.
