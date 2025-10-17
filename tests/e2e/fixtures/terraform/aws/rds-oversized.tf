# Issue: RDS instance over-provisioned for dev environment
# Severity: MEDIUM
# Expected Fix: Downgrade to db.t3.medium

resource "aws_db_instance" "test_mysql" {
  identifier = "ops-agent-test-db"

  # ❌ Too large for test environment!
  instance_class = "db.r5.4xlarge"  # 16 vCPU, 128GB RAM - way too much!

  engine         = "mysql"
  engine_version = "8.0.35"

  allocated_storage = 1000  # ❌ 1TB for test data?

  username = "admin"
  password = "test-password-123"  # In real scenario, use secrets

  skip_final_snapshot = true

  tags = {
    Environment = "test"
    ManagedBy   = "terraform"
    Issue       = "oversized-instance"
  }
}
