# Issue: Kinesis stream under-provisioned
# Severity: HIGH
# Expected Fix: Increase shard count based on throughput

resource "aws_kinesis_stream" "test_stream" {
  name = "ops-agent-test-stream"

  # ❌ Only 1 shard but high throughput requirement!
  shard_count = 1  # Can only handle 1MB/s write, 2MB/s read

  retention_period = 24

  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
  ]

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
    Issue       = "under-provisioned-shards"
    # Note: This is production but only 1 shard!
  }
}
