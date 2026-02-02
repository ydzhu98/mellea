# Testing the KG Library

## Running Tests

### Quick Start (All Tests)

Run all tests (unit + mock tests will pass, Neo4j tests will skip if no instance):

```bash
uv run pytest test/contribs/kg/ -v
```

### Neo4j Integration Tests

#### Option 1: Use Existing Neo4j Instance

If you have Neo4j running, set the password:

```bash
# Set your Neo4j password
export NEO4J_PASSWORD="your_actual_password"

# Run Neo4j integration tests
uv run pytest test/contribs/kg/test_neo4j_backend.py -v
```

#### Option 2: Start Neo4j with Docker

```bash
# Start Neo4j in Docker
docker run --rm -d -p 7687:7687 -p 7474:7474 \
    --name neo4j-test \
    -e NEO4J_AUTH=neo4j/testpassword \
    neo4j:latest

# Wait for Neo4j to start (about 30 seconds)
sleep 30

# Run tests (uses default password "testpassword")
uv run pytest test/contribs/kg/test_neo4j_backend.py -v

# Clean up
docker stop neo4j-test
```

### Environment Variables

The tests use these environment variables (with defaults):

- `NEO4J_URI`: Connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Username (default: `neo4j`)
- `NEO4J_PASSWORD`: Password (default: `testpassword`)

Example with all variables:

```bash
export NEO4J_URI="bolt://my-server:7687"
export NEO4J_USER="admin"
export NEO4J_PASSWORD="secret123"

uv run pytest test/contribs/kg/test_neo4j_backend.py -v
```

## Test Categories

### Unit Tests (No Database Required)

```bash
# Data structure tests
uv run pytest test/contribs/kg/test_base.py -v

# Mock backend tests
uv run pytest test/contribs/kg/test_mock_backend.py -v
```

These always pass without any database.

### Integration Tests (Require Neo4j)

```bash
# Neo4j backend tests (requires running instance)
uv run pytest test/contribs/kg/test_neo4j_backend.py -v
```

These will skip gracefully if:
- Neo4j is not running
- Authentication fails
- Connection cannot be established

## Expected Results

### Without Neo4j Running

```
========================= 18 passed, 12 skipped =========================
```

- 9 tests: Data structures
- 7 tests: Mock backend
- 2 tests: Neo4j backend creation/close (don't require connection)
- 12 skipped: Integration tests requiring Neo4j

### With Neo4j Running (Correct Password)

```
========================= 30 passed =========================
```

All tests pass!

## Troubleshooting

### Tests Are Skipped

**Symptom**: `12 skipped` in test results

**Causes**:
1. Neo4j not running → Check with `nc -zv localhost 7687`
2. Wrong password → Set correct password with `export NEO4J_PASSWORD="..."`
3. Connection refused → Neo4j may still be starting (wait 30s after Docker start)

### Authentication Errors

**Symptom**: Tests skip with "unauthorized" or "authentication failure"

**Solution**:
```bash
# Check what password Neo4j is using
# If you started with Docker, it's the password in NEO4J_AUTH

# Set the correct password
export NEO4J_PASSWORD="your_correct_password"

# Run tests again
uv run pytest test/contribs/kg/test_neo4j_backend.py -v
```

### Connection Refused

**Symptom**: Tests skip with "Connection refused"

**Solutions**:
1. Check Neo4j is running: `nc -zv localhost 7687`
2. If using Docker, wait 30 seconds after starting
3. Check Neo4j logs: `docker logs neo4j-test`

### Slow Tests

**Symptom**: Tests take a long time

This is normal! Each test:
- Clears the database
- Creates test data
- Runs queries
- Cleans up

Integration tests typically take 20-30 seconds total.

## CI/CD

For CI/CD pipelines, use the Docker approach:

```yaml
# GitHub Actions example
- name: Start Neo4j
  run: |
    docker run --rm -d -p 7687:7687 -p 7474:7474 \
      --name neo4j-test \
      -e NEO4J_AUTH=neo4j/testpassword \
      neo4j:latest
    sleep 30

- name: Run tests
  run: uv run pytest test/contribs/kg/ -v

- name: Stop Neo4j
  run: docker stop neo4j-test
```

## Development Workflow

### Quick Feedback Loop

During development, run only unit tests for fast feedback:

```bash
# Fast: ~1 second
uv run pytest test/contribs/kg/test_base.py test/contribs/kg/test_mock_backend.py -v
```

### Before Committing

Run all tests including integration:

```bash
# Start Neo4j if needed
docker run --rm -d -p 7687:7687 -p 7474:7474 \
    --name neo4j-test \
    -e NEO4J_AUTH=neo4j/testpassword \
    neo4j:latest

sleep 30

# Run all tests
uv run pytest test/contribs/kg/ -v

# Clean up
docker stop neo4j-test
```
