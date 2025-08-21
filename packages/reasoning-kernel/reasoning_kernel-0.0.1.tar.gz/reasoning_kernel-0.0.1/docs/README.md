# Reasoning Kernel Documentation

This directory contains the comprehensive documentation for the Reasoning Kernel, built with [Mintlify](https://mintlify.com).

## 📖 Documentation Structure

The documentation is organized following Mintlify best practices:

### Core Documentation

- **Introduction** (`introduction.mdx`) - Overview and key features
- **Quickstart** (`quickstart.mdx`) - Get started in 10 minutes
- **Installation** (`installation.mdx`) - Complete installation guide
- **Configuration** (`configuration.mdx`) - Configuration reference

### Core Concepts

- **MSA Framework** (`concepts/msa-framework.mdx`) - Model Synthesis Architecture
- **Thinking Exploration** (`concepts/thinking-exploration.mdx`) - Dynamic reasoning exploration
- **Semantic Kernel** (`concepts/semantic-kernel.mdx`) - Agent architecture
- **Architecture** (`concepts/architecture.mdx`) - System architecture overview

### API Reference

- **Overview** (`api/overview.mdx`) - API introduction and authentication
- **REST API** (`api/`) - Complete REST API reference
- **Python SDK** (`sdk/`) - Native Python SDK documentation
- **Agents** (`agents/`) - Semantic Kernel agent interfaces

### Guides & Examples

- **Guides** (`guides/`) - Step-by-step implementation guides
- **Examples** (`examples/`) - Real-world usage examples
- **Integration** (`integration/`) - Service integration guides

### Research

- **MSA Paper** (`research/msa-paper.md`) - Research foundation
- **Benchmarks** (`research/benchmarks.md`) - Performance evaluations
- **Implementation Notes** (`research/implementation-notes.md`) - Technical details

## 🚀 Local Development

### Prerequisites

- Node.js 18+ or Python 3.12+
- Mintlify CLI

### Setup

1. **Install Mintlify CLI**:

   ```bash
   npm install -g mintlify
   ```

2. **Clone the repository**:

   ```bash
   git clone https://github.com/qredence/reasoning-kernel.git
   cd reasoning-kernel/docs
   ```

3. **Start the development server**:

   ```bash
   mintlify dev
   ```

4. **Open in browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Making Changes

1. **Edit MDX files** in the docs directory
2. **Update navigation** in `mint.json` or `docs.json`
3. **Add new pages** and reference them in navigation
4. **Preview changes** with `mintlify dev`
5. **Deploy** with `mintlify deploy`

## 📁 File Organization

```
docs/
├── mint.json                 # Mintlify configuration
├── docs.json                 # Alternative configuration  
├── introduction.mdx          # Main introduction page
├── quickstart.mdx           # Getting started guide
├── installation.mdx         # Installation instructions
├── configuration.mdx        # Configuration reference
├── concepts/                # Core concepts
│   ├── msa-framework.mdx
│   ├── thinking-exploration.mdx
│   ├── semantic-kernel.mdx
│   └── architecture.mdx
├── api/                     # API documentation
│   ├── overview.mdx
│   ├── authentication.mdx
│   ├── reasoning.mdx
│   └── ...
├── sdk/                     # Python SDK docs
├── guides/                  # Implementation guides
├── examples/                # Usage examples
├── integration/             # Integration guides
├── research/                # Research documentation
└── static/                  # Static assets
    ├── images/
    ├── logos/
    └── ...
```

## ✅ Documentation Standards

### Writing Guidelines

1. **Clear, concise language** appropriate for technical audiences
2. **Second person ("you")** for instructions and procedures
3. **Active voice** over passive voice
4. **Present tense** for current states, future tense for outcomes
5. **Consistent terminology** throughout all documentation

### Content Organization

1. **Lead with most important information** (inverted pyramid)
2. **Progressive disclosure** - basic concepts before advanced
3. **Numbered steps** for procedures
4. **Prerequisites and context** before instructions
5. **Expected outcomes** for major steps
6. **Next steps** or related information at section end

### MDX Components

Use Mintlify components for enhanced documentation:

```mdx
<Tip>
Pro tips and best practices
</Tip>

<Warning>
Important cautions and breaking changes
</Warning>

<Info>
Neutral contextual information
</Info>

<Check>
Success confirmations and achievements
</Check>

<CardGroup cols={2}>
  <Card title="Feature" icon="icon" href="/link">
    Description of the feature or guide
  </Card>
</CardGroup>

<Tabs>
  <Tab title="Python">
    Python code examples
  </Tab>
  <Tab title="JavaScript">
    JavaScript code examples
  </Tab>
</Tabs>

<Steps>
  <Step title="First Step">
    Instructions for the first step
  </Step>
  <Step title="Second Step">
    Instructions for the second step
  </Step>
</Steps>
```

### Code Examples

1. **Multiple languages** when applicable
2. **Complete, runnable examples**
3. **Proper syntax highlighting**
4. **Comments explaining complex logic**
5. **Error handling included**

### API Documentation

1. **Clear endpoint descriptions**
2. **Request/response examples**
3. **Parameter documentation** with types and requirements
4. **Error codes and handling**
5. **Authentication examples**

## 🔧 Configuration

### Mintlify Configuration (`mint.json`)

The main configuration file includes:

- **Navigation structure** with logical grouping
- **Branding** (colors, logos, favicon)
- **Theme settings** and appearance
- **API playground** configuration
- **Social links** and footer

### Features Enabled

- ✅ **Interactive API playground**
- ✅ **Code syntax highlighting**
- ✅ **Dark/light mode toggle**
- ✅ **Search functionality**
- ✅ **Social media integration**
- ✅ **Mobile-responsive design**
- ✅ **SEO optimization**

## 📚 Content Guidelines

### Page Structure

Each documentation page should include:

1. **Frontmatter** with title and description
2. **Introduction** explaining the page's purpose
3. **Prerequisites** if applicable
4. **Main content** with clear sections
5. **Examples** demonstrating concepts
6. **Next steps** linking to related content

### Code Examples

```mdx
<CodeGroup>
```python Python
from reasoning_kernel import ReasoningKernel

kernel = ReasoningKernel()
result = await kernel.reason("Your scenario")
```

```javascript JavaScript
const response = await fetch('/api/reasoning', {
  method: 'POST',
  body: JSON.stringify({ scenario: 'Your scenario' })
});
```

```bash cURL
curl -X POST "https://api.reasoning-kernel.com/v1/reasoning" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"scenario": "Your scenario"}'
```

</CodeGroup>
```

### Cross-References

Link related content using:

```mdx
- Relative links: [Configuration Guide](/configuration)
- Card links: <Card title="Title" href="/link">Description</Card>
- In-text references: See the [API Overview](/api/overview) for details
```

## 🚀 Deployment

### Automatic Deployment

Documentation is automatically deployed on:

- **Push to main branch** triggers production deployment
- **Pull requests** create preview deployments
- **Staging environment** for testing changes

### Manual Deployment

```bash
# Deploy to production
mintlify deploy

# Deploy with custom domain
mintlify deploy --domain docs.reasoning-kernel.com
```

## 🤝 Contributing

### Contribution Workflow

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the guidelines above
3. **Test locally** with `mintlify dev`
4. **Submit a pull request** with clear description
5. **Address review feedback** if needed

### Review Checklist

- [ ] Content follows writing guidelines
- [ ] Code examples are complete and tested
- [ ] Links work correctly
- [ ] MDX components used appropriately
- [ ] Navigation updated if new pages added
- [ ] Screenshots updated if UI changed
- [ ] No broken links or typos

## 📞 Support

For documentation questions or issues:

- **GitHub Issues**: [Create an issue](https://github.com/qredence/reasoning-kernel/issues)
- **Discord**: [Join our community](https://discord.gg/reasoning-kernel)
- **Email**: [docs@qredence.com](mailto:docs@qredence.com)

---

**Built with ❤️ using [Mintlify](https://mintlify.com)**
