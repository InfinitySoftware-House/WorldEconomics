# Contributing to World Economics Simulator

Thank you for your interest in contributing to the World Economics Simulator! This project aims to provide a sophisticated macroeconomic simulation tool, and we welcome contributions from the community.

## Project Vision

The World Economics Simulator is being developed as a core component of the **StartUp Business Tycoon Simulation Game**. This algorithm will power the dynamic global economy that players interact with, making the game world more realistic, challenging, and engaging.

### Integration into StartUp Business

In the future versions of StartUp Business, this simulator will:

- **Dynamic World Economy**: Generate realistic macroeconomic conditions that affect player businesses (interest rates, inflation, unemployment, trade flows)
- **Market Cycles**: Create natural boom and bust cycles that players must navigate
- **International Expansion**: Model trade dynamics when players expand to different countries
- **Policy Impact**: Simulate how government policies affect business conditions in different regions
- **Strategic Depth**: Provide players with economic indicators to inform their business decisions
- **Competitive Challenge**: Create varying difficulty levels based on economic conditions in different countries and time periods

By contributing to this simulator, you're helping shape the economic foundation of the game and making it more immersive for players worldwide.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Areas for Contribution](#areas-for-contribution)
- [Questions and Support](#questions-and-support)

## Ways to Contribute

There are many ways you can contribute to this project:

- **Report bugs**: Help us identify and fix issues
- **Suggest enhancements**: Propose new features or improvements to existing ones
- **Improve documentation**: Fix typos, clarify explanations, or add examples
- **Add test cases**: Create new seed files with interesting scenarios
- **Write code**: Fix bugs, implement new features, or optimize existing code
- **Share analysis**: Run simulations and share interesting findings
- **Improve visualization**: Enhance the plotting and data presentation

## Getting Started

### Prerequisites

1. Python 3.7 or higher
2. Basic understanding of economics (helpful but not required)
3. Git for version control

### Setting Up Your Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StartUpBusiness.git
cd StartUpBusiness/Scripts/WorldEcomics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run a test simulation to ensure everything works:
```bash
python world_economics.py --seed sample_seed.json --years 10 --out test_run
```

4. Verify the output files were created in the `test_run` directory

## Development Workflow

### Before Making Changes

1. **Check existing issues**: Look through the issue tracker to see if someone else is already working on something similar
2. **Create an issue**: For major changes, open an issue first to discuss your proposed changes
3. **Fork the repository**: Create your own fork to work on

### Making Changes

1. **Create a branch**: Use descriptive branch names
   - Feature: `feature/add-regional-trade-blocks`
   - Bug fix: `fix/inflation-calculation-overflow`
   - Documentation: `docs/improve-seed-file-examples`

2. **Make your changes**: Write clean, readable code with appropriate comments

3. **Test your changes**: Run simulations with different seed files to ensure your changes work correctly
   ```bash
   python world_economics.py --seed sample_seed.json --years 30 --runs 3
   ```

4. **Document your changes**: Update the README.md if you add new features or change behavior

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use meaningful variable names
- Keep functions focused and modular
- Add docstrings for new functions and classes
- Use type hints where appropriate

### Example Function Style

```python
def calculate_trade_flow(country_a: Country, country_b: Country, distance: float) -> float:
    """
    Calculate bilateral trade flow between two countries using gravity model.
    
    Args:
        country_a: Exporting country
        country_b: Importing country
        distance: Distance between countries in kilometers
        
    Returns:
        Trade flow value in billions
    """
    base_flow = GRAVITY_K * (country_a.gdp * country_b.gdp) / (distance ** DISTANCE_DECAY)
    return base_flow
```

### Comments

- Use comments to explain **why**, not **what**
- Document economic assumptions and calibrations
- Reference academic papers or sources for model specifications where applicable

### Constants

- Define all calibration parameters at the top of the file
- Use UPPER_CASE for constants
- Add comments explaining the economic meaning of parameters

## Submitting Changes

### Pull Request Process

1. **Update your branch**: Ensure your fork is up-to-date with the main repository
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a pull request**: Provide a clear description of your changes
   - What problem does it solve?
   - How did you test it?
   - What are the implications for existing simulations?

3. **PR Description Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - Describe how you tested your changes
   - Include example commands and seed files used
   
   ## Economic Rationale
   - Explain the economic reasoning behind model changes
   
   ## Breaking Changes
   - List any breaking changes
   - Suggest migration path if applicable
   ```

4. **Code review**: Be responsive to feedback and make requested changes

5. **Merge**: Once approved, your changes will be merged

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to reproduce the bug
- **Seed file**: Attach or link to the seed file that causes the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **System information**: Python version, OS, installed packages
- **Output**: Relevant error messages or logs

### Feature Requests

For feature requests, please include:

- **Problem statement**: What problem would this feature solve?
- **Proposed solution**: How would you like to see it implemented?
- **Alternatives considered**: Other approaches you've thought about
- **Use case**: Example scenarios where this would be useful

### Issue Template Example

```markdown
## Bug Report / Feature Request

**Type**: [Bug / Feature Request / Enhancement]

**Description**:
Clear description of the issue or feature

**Steps to Reproduce** (for bugs):
1. Run command: `python world_economics.py --seed xyz.json --years 50`
2. Observe output in year 35
3. Notice that debt_to_gdp becomes negative

**Expected Behavior**:
Debt ratio should remain non-negative

**System Information**:
- Python version: 3.9.7
- OS: macOS 12.3
- matplotlib version: 3.5.1
```

## Areas for Contribution

Here are some specific areas where contributions would be particularly valuable:

### Model Enhancements

- **Trade dynamics**: More sophisticated trade models (e.g., input-output linkages)
- **Financial sector**: Banking crises, credit cycles
- **Climate economics**: Carbon pricing, green technology adoption
- **Labor markets**: Migration flows, skill composition
- **Inequality**: Within-country income distribution
- **Exchange rates**: Currency dynamics and forex interventions

### Technical Improvements

- **Performance optimization**: Speed up simulations for large country sets
- **Parallel processing**: Run multiple simulations in parallel
- **Interactive mode**: Real-time parameter adjustment
- **Web interface**: Browser-based simulation and visualization
- **Data validation**: Better input validation and error messages

### Visualization & Analysis

- **Interactive plots**: Use plotly or bokeh for interactive visualizations
- **Comparison tools**: Compare multiple simulation runs
- **Statistical analysis**: Add summary statistics and regression analysis
- **Animation**: Animate economic indicators over time
- **Network graphs**: Visualize trade networks

### Documentation & Testing

- **Tutorial notebooks**: Jupyter notebooks with guided examples
- **Video tutorials**: Screencasts explaining the simulator
- **More seed files**: Pre-configured scenarios (e.g., "2008 Financial Crisis", "Oil Shock")
- **Validation studies**: Compare simulations against historical data
- **Unit tests**: Test individual functions and components

### Economic Scenarios

Create seed files for interesting historical or hypothetical scenarios:

- Post-WWII reconstruction
- Asian Financial Crisis (1997)
- European debt crisis
- Oil shocks of the 1970s
- Rise of emerging markets
- Alternative history scenarios

## Questions and Support

If you have questions or need help:

- **Issues**: Open an issue with the "question" label
- **Documentation**: Check the README.md first
- **Email**: Contact the maintainers (check the main repository)

## Code of Conduct

### Our Standards

We are committed to providing a welcoming and inclusive environment. We expect all contributors to:

- Be respectful and considerate in communication
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the project and community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information without permission
- Other conduct that would be inappropriate in a professional setting

## Recognition

Contributors who make significant contributions will be:

- Listed in the project's contributors file
- Acknowledged in release notes
- Credited in academic papers using this tool (where appropriate)

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to the World Economics Simulator! Your efforts help make economic modeling more accessible and powerful for everyone.

