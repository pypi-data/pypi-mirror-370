"""Tests for the IAM policy analyzer."""

import pytest
from pathlib import Path

from iamx.core.analyzer import PolicyAnalyzer
from iamx.core.models import AnalysisConfig, Severity
from iamx.core.parser import PolicyParser


class TestPolicyParser:
    """Test the policy parser."""
    
    def test_parse_valid_policy(self):
        """Test parsing a valid IAM policy."""
        parser = PolicyParser()
        policy_content = '''
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "s3:GetObject",
              "Resource": "arn:aws:s3:::my-bucket/*"
            }
          ]
        }
        '''
        
        policy = parser.parse_string(policy_content)
        assert policy["Version"] == "2012-10-17"
        assert len(policy["Statement"]) == 1
        assert policy["Statement"][0]["Effect"] == "Allow"
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        parser = PolicyParser()
        with pytest.raises(Exception):
            parser.parse_string("{ invalid json }")
    
    def test_parse_missing_version(self):
        """Test parsing policy without version."""
        parser = PolicyParser()
        policy_content = '''
        {
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "s3:GetObject",
              "Resource": "arn:aws:s3:::my-bucket/*"
            }
          ]
        }
        '''
        
        with pytest.raises(Exception):
            parser.parse_string(policy_content)


class TestPolicyAnalyzer:
    """Test the policy analyzer."""
    
    def test_analyze_admin_policy(self):
        """Test analyzing an admin policy with overly permissive actions."""
        analyzer = PolicyAnalyzer()
        
        policy_content = '''
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": [
                "iam:*",
                "s3:*",
                "ec2:*"
              ],
              "Resource": "*"
            }
          ]
        }
        '''
        
        result = analyzer.analyze_string(policy_content)
        
        # Should have findings
        assert len(result.findings) > 0
        
        # Should have critical findings for overly permissive actions
        critical_findings = [f for f in result.findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) > 0
        
        # Should have high risk score
        assert result.risk_score > 5.0
        
        # Should fail analysis
        assert not result.passed
    
    def test_analyze_secure_policy(self):
        """Test analyzing a secure policy with least-privilege permissions."""
        analyzer = PolicyAnalyzer()
        
        policy_content = '''
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": [
                "s3:GetObject",
                "s3:ListBucket"
              ],
              "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
              ]
            }
          ]
        }
        '''
        
        result = analyzer.analyze_string(policy_content)
        
        # Should have low risk score
        assert result.risk_score < 3.0
        
        # Should pass analysis
        assert result.passed
    
    def test_analyze_with_config(self):
        """Test analyzing with custom configuration."""
        config = AnalysisConfig(
            fail_on_severity=Severity.MEDIUM,
            include_info=True,
            max_findings_per_category=5
        )
        
        analyzer = PolicyAnalyzer(config)
        
        policy_content = '''
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "s3:*",
              "Resource": "*"
            }
          ]
        }
        '''
        
        result = analyzer.analyze_string(policy_content)
        
        # Should have findings
        assert len(result.findings) > 0
        
        # Should fail due to high severity findings
        assert not result.passed
    
    def test_analyze_file(self, tmp_path):
        """Test analyzing a policy file."""
        analyzer = PolicyAnalyzer()
        
        # Create a temporary policy file
        policy_file = tmp_path / "test-policy.json"
        policy_content = '''
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "iam:*",
              "Resource": "*"
            }
          ]
        }
        '''
        policy_file.write_text(policy_content)
        
        result = analyzer.analyze_file(str(policy_file))
        
        # Should have findings
        assert len(result.findings) > 0
        assert result.metadata.filename == "test-policy.json"
    
    def test_analyze_multiple_files(self, tmp_path):
        """Test analyzing multiple policy files."""
        analyzer = PolicyAnalyzer()
        
        # Create temporary policy files
        policies = [
            ('admin-policy.json', '''
            {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Effect": "Allow",
                  "Action": "iam:*",
                  "Resource": "*"
                }
              ]
            }
            '''),
            ('secure-policy.json', '''
            {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Effect": "Allow",
                  "Action": "s3:GetObject",
                  "Resource": "arn:aws:s3:::my-bucket/*"
                }
              ]
            }
            ''')
        ]
        
        policy_files = []
        for filename, content in policies:
            policy_file = tmp_path / filename
            policy_file.write_text(content)
            policy_files.append(str(policy_file))
        
        result = analyzer.analyze_multiple_files(policy_files)
        
        # Should have results for both files
        assert len(result.results) == 2
        assert result.total_policies == 2
        
        # Should have at least one failed policy
        assert result.failed_policies > 0


class TestSeverityLevels:
    """Test severity level handling."""
    
    def test_severity_ordering(self):
        """Test that severity levels are ordered correctly."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"
    
    def test_severity_comparison(self):
        """Test severity level comparisons."""
        # Critical should be higher than high
        config = AnalysisConfig(fail_on_severity=Severity.HIGH)
        analyzer = PolicyAnalyzer(config)
        
        # Policy with only critical findings should fail
        policy_content = '''
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "iam:*",
              "Resource": "*"
            }
          ]
        }
        '''
        
        result = analyzer.analyze_string(policy_content)
        assert not result.passed
