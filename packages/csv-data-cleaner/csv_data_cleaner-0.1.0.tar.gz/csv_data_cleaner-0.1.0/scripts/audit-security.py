#!/usr/bin/env python3
"""
Security Audit Script for CSV Data Cleaner
Checks dependencies, security vulnerabilities, and compliance
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityAudit:
    """Security audit for CSV Data Cleaner"""

    def __init__(self):
        self.audit_results = {
            'dependencies': {},
            'vulnerabilities': [],
            'security_issues': [],
            'recommendations': [],
            'compliance': {},
            'overall_score': 0
        }

    def check_dependencies(self) -> Dict[str, Any]:
        """Check all dependencies for security vulnerabilities"""
        logger.info("Checking dependencies for security vulnerabilities...")

        try:
            # Check if safety is installed
            result = subprocess.run(['safety', 'check', '--json'],
                                  capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                self.audit_results['vulnerabilities'] = vulnerabilities

                # Count vulnerabilities by severity
                severity_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
                for vuln in vulnerabilities:
                    severity = vuln.get('severity', 'UNKNOWN')
                    if severity in severity_counts:
                        severity_counts[severity] += 1

                self.audit_results['dependencies']['vulnerability_summary'] = severity_counts

                # Calculate security score
                total_vulns = sum(severity_counts.values())
                if total_vulns == 0:
                    self.audit_results['overall_score'] = 100
                else:
                    # Penalize based on severity
                    score = 100
                    score -= severity_counts['LOW'] * 1
                    score -= severity_counts['MEDIUM'] * 5
                    score -= severity_counts['HIGH'] * 15
                    score -= severity_counts['CRITICAL'] * 30
                    self.audit_results['overall_score'] = max(0, score)

                logger.info(f"Found {total_vulns} vulnerabilities")
                for severity, count in severity_counts.items():
                    if count > 0:
                        logger.warning(f"  {severity}: {count}")

            else:
                logger.warning("Safety check failed, trying alternative method...")
                self._check_dependencies_alternative()

        except FileNotFoundError:
            logger.warning("Safety not installed, using alternative method...")
            self._check_dependencies_alternative()
        except Exception as e:
            logger.error(f"Error checking dependencies: {str(e)}")
            self.audit_results['security_issues'].append(f"Dependency check failed: {str(e)}")

    def _check_dependencies_alternative(self):
        """Alternative dependency checking method"""
        logger.info("Using alternative dependency checking method...")

        # Check requirements.txt
        project_root = Path(__file__).parent.parent  # Go up one level to project root
        requirements_file = project_root / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            self.audit_results['dependencies']['requirements'] = dependencies
            logger.info(f"Found {len(dependencies)} dependencies in requirements.txt")

        # Check pyproject.toml
        pyproject_file = project_root / "pyproject.toml"
        if pyproject_file.exists():
            logger.info("Found pyproject.toml - dependencies listed in project configuration")

    def check_code_security(self) -> Dict[str, Any]:
        """Check code for common security issues"""
        logger.info("Checking code for security issues...")

        security_issues = []

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'sk-[a-zA-Z0-9]{48}',
            r'sk-ant-[a-zA-Z0-9]{48}'
        ]

        # Check Python files for security issues
        project_root = Path(__file__).parent.parent  # Go up one level to project root
        python_files = list(project_root.rglob('*.py'))
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for hardcoded secrets
                for pattern in secret_patterns:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        security_issues.append({
                            'file': str(file_path),
                            'issue': 'Hardcoded secret found',
                            'pattern': pattern,
                            'severity': 'HIGH'
                        })

                # Check for dangerous imports
                dangerous_imports = ['pickle', 'marshal', 'eval', 'exec']
                for dangerous_import in dangerous_imports:
                    if f'import {dangerous_import}' in content or f'from {dangerous_import}' in content:
                        security_issues.append({
                            'file': str(file_path),
                            'issue': f'Dangerous import: {dangerous_import}',
                            'severity': 'MEDIUM'
                        })

            except Exception as e:
                logger.warning(f"Could not read {file_path}: {str(e)}")

        self.audit_results['security_issues'].extend(security_issues)
        logger.info(f"Found {len(security_issues)} code security issues")

    def check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions for security"""
        logger.info("Checking file permissions...")

        permission_issues = []

        # Check for overly permissive files
        project_root = Path(__file__).parent.parent  # Go up one level to project root
        sensitive_files = [
            'requirements.txt',
            'pyproject.toml',
            'setup.py',
            '.env',
            'config.json'
        ]

        for file_name in sensitive_files:
            file_path = project_root / file_name
            if file_path.exists():
                try:
                    stat = file_path.stat()
                    mode = stat.st_mode & 0o777

                    # Check if file is world-writable
                    if mode & 0o002:
                        permission_issues.append({
                            'file': file_name,
                            'issue': 'File is world-writable',
                            'permission': oct(mode),
                            'severity': 'MEDIUM'
                        })

                    # Check if file is world-readable (for sensitive files)
                    if file_name in ['.env', 'config.json'] and mode & 0o004:
                        permission_issues.append({
                            'file': file_name,
                            'issue': 'Sensitive file is world-readable',
                            'permission': oct(mode),
                            'severity': 'HIGH'
                        })

                except Exception as e:
                    logger.warning(f"Could not check permissions for {file_name}: {str(e)}")

        self.audit_results['security_issues'].extend(permission_issues)
        logger.info(f"Found {len(permission_issues)} permission issues")

    def check_data_privacy(self) -> Dict[str, Any]:
        """Check data privacy compliance"""
        logger.info("Checking data privacy compliance...")

        privacy_issues = []

        # Check for data handling practices
        project_root = Path(__file__).parent.parent  # Go up one level to project root
        python_files = list(project_root.rglob('*.py'))
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for potential data exposure
                if 'print(' in content and any(keyword in content for keyword in ['password', 'api_key', 'token', 'secret']):
                    privacy_issues.append({
                        'file': str(file_path),
                        'issue': 'Potential sensitive data exposure in print statements',
                        'severity': 'MEDIUM'
                    })

                # Check for logging of sensitive data
                if 'logging.' in content and any(keyword in content for keyword in ['password', 'api_key', 'token', 'secret']):
                    privacy_issues.append({
                        'file': str(file_path),
                        'issue': 'Potential sensitive data logging',
                        'severity': 'MEDIUM'
                    })

            except Exception as e:
                logger.warning(f"Could not read {file_path}: {str(e)}")

        self.audit_results['security_issues'].extend(privacy_issues)
        logger.info(f"Found {len(privacy_issues)} privacy issues")

    def generate_recommendations(self):
        """Generate security recommendations"""
        logger.info("Generating security recommendations...")

        recommendations = []

        # Dependency recommendations
        if self.audit_results['vulnerabilities']:
            recommendations.append({
                'category': 'Dependencies',
                'priority': 'HIGH',
                'recommendation': 'Update vulnerable dependencies to latest secure versions',
                'action': 'Run: pip install --upgrade <package_name>'
            })

        # Code security recommendations
        code_issues = [issue for issue in self.audit_results['security_issues']
                      if issue.get('severity') in ['HIGH', 'CRITICAL']]
        if code_issues:
            recommendations.append({
                'category': 'Code Security',
                'priority': 'HIGH',
                'recommendation': 'Fix high-severity code security issues',
                'action': 'Review and fix identified security issues in code'
            })

        # General recommendations
        if self.audit_results['overall_score'] < 80:
            recommendations.append({
                'category': 'General',
                'priority': 'MEDIUM',
                'recommendation': 'Implement additional security measures',
                'action': 'Consider adding security scanning to CI/CD pipeline'
            })

        # Always recommend security best practices
        recommendations.extend([
            {
                'category': 'Best Practices',
                'priority': 'MEDIUM',
                'recommendation': 'Use environment variables for sensitive configuration',
                'action': 'Move API keys and secrets to environment variables'
            },
            {
                'category': 'Best Practices',
                'priority': 'MEDIUM',
                'recommendation': 'Implement input validation and sanitization',
                'action': 'Add comprehensive input validation for all user inputs'
            },
            {
                'category': 'Best Practices',
                'priority': 'LOW',
                'recommendation': 'Regular security audits',
                'action': 'Schedule regular security audits and dependency updates'
            }
        ])

        self.audit_results['recommendations'] = recommendations

    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete security audit"""
        logger.info("Starting comprehensive security audit...")

        # Run all audit checks
        self.check_dependencies()
        self.check_code_security()
        self.check_file_permissions()
        self.check_data_privacy()
        self.generate_recommendations()

        # Calculate final compliance score
        total_issues = len(self.audit_results['security_issues'])
        high_severity_issues = len([issue for issue in self.audit_results['security_issues']
                                   if issue.get('severity') == 'HIGH'])

        self.audit_results['compliance'] = {
            'total_issues': total_issues,
            'high_severity_issues': high_severity_issues,
            'security_score': self.audit_results['overall_score'],
            'status': 'PASS' if self.audit_results['overall_score'] >= 80 else 'FAIL'
        }

        # Save results
        project_root = Path(__file__).parent.parent  # Go up one level to project root
        results_file = project_root / 'security_audit_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)

        logger.info("Security audit completed. Results saved to security_audit_results.json")
        return self.audit_results

def main():
    """Main security audit function"""
    logger.info("CSV Data Cleaner Security Audit")
    logger.info("=" * 40)

    audit = SecurityAudit()

    try:
        results = audit.run_full_audit()

        # Print summary
        print("\n" + "=" * 40)
        print("SECURITY AUDIT RESULTS")
        print("=" * 40)

        print(f"\nOverall Security Score: {results['overall_score']}/100")
        print(f"Status: {results['compliance']['status']}")

        print(f"\nIssues Found:")
        print(f"  Total Issues: {results['compliance']['total_issues']}")
        print(f"  High Severity: {results['compliance']['high_severity_issues']}")

        if results['dependencies'].get('vulnerability_summary'):
            print(f"\nDependency Vulnerabilities:")
            for severity, count in results['dependencies']['vulnerability_summary'].items():
                if count > 0:
                    print(f"  {severity}: {count}")

        if results['recommendations']:
            print(f"\nTop Recommendations:")
            high_priority = [rec for rec in results['recommendations'] if rec['priority'] == 'HIGH']
            for rec in high_priority[:3]:
                print(f"  - {rec['recommendation']}")

        return 0 if results['compliance']['status'] == 'PASS' else 1

    except Exception as e:
        logger.error(f"Security audit failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
