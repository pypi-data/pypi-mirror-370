# Chaos Engineering Test Suite

## Overview

The KEI-Agent Python SDK includes a comprehensive chaos engineering test suite designed to validate system resilience and fault tolerance under various failure conditions. This suite helps ensure that the system can gracefully handle unexpected failures and maintain core functionality during adverse conditions.

## Test Categories

### 1. Network Chaos Tests (`test_network_chaos.py`)

Tests system resilience under network-related failures:

- **Network Latency Resilience**: Validates behavior under high network latency
- **Connection Failure Resilience**: Tests retry mechanisms and circuit breakers
- **Protocol Failover Mechanisms**: Validates failover between RPC, Stream, Bus, and MCP protocols
- **Packet Loss Handling**: Tests system behavior under packet loss conditions
- **Intermittent Connectivity**: Validates handling of unstable network connections
- **Circuit Breaker Behavior**: Tests circuit breaker patterns under network failures

### 2. Service Dependency Chaos Tests (`test_service_dependency_chaos.py`)

Tests graceful degradation when external services fail:

- **Authentication Service Failure**: Tests fallback authentication mechanisms
- **Metrics Collection Service Outage**: Validates graceful degradation when metrics services are unavailable
- **Configuration Service Unavailability**: Tests fallback to cached configuration
- **Multiple Service Failures**: Tests behavior when multiple services fail simultaneously
- **Service Recovery Patterns**: Validates health checks and recovery mechanisms
- **Graceful Degradation Levels**: Tests different levels of service degradation

### 3. Resource Exhaustion Chaos Tests (`test_resource_exhaustion_chaos.py`)

Tests system behavior under resource constraints:

- **Memory Pressure Resilience**: Validates behavior under high memory usage
- **CPU Pressure Resilience**: Tests performance under CPU constraints
- **Connection Pool Exhaustion**: Tests connection pooling and reuse mechanisms
- **Rate Limiting Backpressure**: Validates rate limiting and backpressure handling
- **Disk Space Constraints**: Tests behavior when disk space is limited
- **Combined Resource Exhaustion**: Tests system under multiple resource constraints

### 4. Configuration Chaos Tests (`test_configuration_chaos.py`)

Tests configuration management resilience:

- **Invalid Configuration Injection**: Tests validation and fallback mechanisms
- **Configuration File Corruption**: Validates handling of corrupted config files
- **Configuration Rollback Mechanisms**: Tests rollback under various failure scenarios
- **Concurrent Configuration Updates**: Tests thread-safe configuration updates
- **Configuration Hot-Reload Failure**: Tests manual reload when file watchers fail

### 5. Security Chaos Tests (`test_security_chaos.py`)

Tests security resilience under attack scenarios:

- **Authentication Token Expiration**: Tests token refresh and fallback mechanisms
- **Certificate Validation Failures**: Tests SSL/TLS certificate handling
- **Security Attack Detection**: Tests detection of malicious patterns
- **Rate Limiting Bypass Attempts**: Tests rate limiting effectiveness
- **Comprehensive Security Resilience**: Tests multiple security vectors simultaneously

## Framework Components

### Core Framework (`chaos_framework.py`)

- **ChaosTest**: Base class for chaos engineering tests
- **ChaosInjector**: Abstract base for chaos injection mechanisms
- **ChaosMetrics**: Metrics collection during chaos tests
- **NetworkChaosInjector**: Network-specific chaos injection
- **ServiceDependencyChaosInjector**: Service dependency chaos injection
- **ResourceExhaustionInjector**: Resource constraint injection

### Metrics Collection (`chaos_metrics.py`)

- **ChaosMetricsCollector**: Collects and analyzes test metrics
- **ResilienceScore**: Calculated resilience scores for components
- Comprehensive reporting and trend analysis
- Performance impact analysis
- Automated recommendations generation

### Integration Framework (`chaos_integration.py`)

- **ChaosTestSuite**: Orchestrates test execution
- CI/CD pipeline integration
- Safe execution mechanisms
- Automated reporting
- Test scheduling and coordination

## Usage

### Running Individual Tests

```bash
# Run network chaos tests
python -m pytest tests/chaos/test_network_chaos.py -v

# Run specific test
python -m pytest tests/chaos/test_network_chaos.py::TestNetworkChaos::test_network_latency_resilience -v

# Run with custom timeout
python -m pytest tests/chaos/test_network_chaos.py --timeout=300 -v
```

### Running Complete Test Suite

```bash
# Run all chaos tests
python tests/chaos/chaos_integration.py

# Run specific categories
python tests/chaos/chaos_integration.py --categories network security

# Run in safe mode (default)
python tests/chaos/chaos_integration.py --safe-mode

# Generate detailed report
python tests/chaos/chaos_integration.py --output chaos-report.json --verbose
```

### CI/CD Integration

The chaos tests are integrated into GitHub Actions workflows:

```yaml
# Scheduled chaos testing
- cron: '0 2 * * *'  # Daily at 2 AM UTC

# Manual trigger with parameters
workflow_dispatch:
  inputs:
    test_categories: 'network,service_dependency,resource_exhaustion'
    safe_mode: true
    environment: 'staging'
```

## Configuration

### Test Configuration

```json
{
  "safe_mode": true,
  "timeout": 300,
  "max_chaos_intensity": 0.5,
  "resource_limits": {
    "max_memory_mb": 100,
    "max_cpu_percent": 50
  },
  "network_chaos": {
    "max_latency_ms": 1000,
    "max_packet_loss": 0.3
  }
}
```

### Environment Variables

- `CHAOS_ENV`: Environment type (development, staging, production)
- `CHAOS_SAFE_MODE`: Enable safe mode (true/false)
- `CHAOS_CATEGORIES`: Comma-separated list of test categories
- `CHAOS_TEST_MODE`: Test execution mode (ci, local, manual)

## Safety Mechanisms

### Pre-Test Safety Checks

- System resource validation (memory, CPU, disk)
- Environment verification
- Service health checks
- Resource threshold validation

### During Test Execution

- Real-time resource monitoring
- Automatic test termination on resource exhaustion
- Graceful chaos injection with controlled intensity
- Continuous system health monitoring

### Post-Test Cleanup

- Automatic resource cleanup
- System stabilization verification
- Resource leak detection
- Process cleanup and verification

## Metrics and Reporting

### Resilience Scores

- **Availability Score**: Based on success rates during chaos
- **Recovery Score**: Based on recovery time after failures
- **Error Handling Score**: Based on error rates during chaos
- **Overall Score**: Weighted average of component scores

### Report Structure

```json
{
  "execution_metadata": {
    "start_time": "2024-01-01T00:00:00Z",
    "duration_seconds": 300,
    "environment": "staging",
    "failed_tests": []
  },
  "chaos_test_results": {
    "summary": {
      "total_tests": 25,
      "overall_resilience_score": 85.2
    },
    "resilience_scores": {
      "network": {"overall_score": 88.5},
      "security": {"overall_score": 82.1}
    }
  },
  "recommendations": [
    "Improve network recovery time with faster health checks",
    "Enhance security error handling mechanisms"
  ]
}
```

### Trend Analysis

- Success rate trends over time
- Recovery time improvements
- Performance impact analysis
- Component resilience evolution

## Best Practices

### Test Development

1. **Start Small**: Begin with simple chaos scenarios
2. **Gradual Intensity**: Increase chaos intensity gradually
3. **Comprehensive Coverage**: Test all critical system components
4. **Real-World Scenarios**: Model actual failure patterns
5. **Automated Validation**: Include automated success criteria

### Production Readiness

1. **Staging First**: Always test in staging before production
2. **Gradual Rollout**: Start with limited scope in production
3. **Monitoring**: Ensure comprehensive monitoring during tests
4. **Rollback Plans**: Have immediate rollback capabilities
5. **Team Coordination**: Coordinate with operations teams

### Continuous Improvement

1. **Regular Execution**: Run chaos tests regularly
2. **Metric Tracking**: Track resilience metrics over time
3. **Failure Analysis**: Analyze and learn from failures
4. **System Hardening**: Implement improvements based on results
5. **Documentation**: Keep test scenarios and results documented

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Resource Constraints**: Check system resources before testing
3. **Permission Issues**: Ensure proper permissions for file operations
4. **Network Issues**: Verify network connectivity for service tests
5. **Timeout Errors**: Adjust timeout values for slower systems

### Debug Mode

```bash
# Run with debug logging
python tests/chaos/chaos_integration.py --verbose

# Run single test with detailed output
python -m pytest tests/chaos/test_network_chaos.py -v -s --tb=long
```

## Contributing

### Adding New Chaos Tests

1. Create test class inheriting from appropriate base
2. Implement chaos injection mechanisms
3. Add comprehensive assertions
4. Include proper cleanup
5. Update documentation

### Extending Framework

1. Follow existing patterns and conventions
2. Add comprehensive error handling
3. Include safety mechanisms
4. Add metrics collection
5. Update integration framework

For more information, see the individual test files and framework documentation.
