#!/usr/bin/env python3
"""Package auditor for understanding project structure before documentation builds."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import click


class PackageAuditor:
    """Audit Python packages to understand scope before documentation builds."""

    def __init__(self, root_path: Path):
        """Initialize auditor with root path."""
        self.root_path = Path(root_path)
        self.audit_data = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "packages": {},
            "summary": {},
        }

    def audit_package(self, package_path: Path) -> Dict:
        """Audit a single package."""
        package_name = package_path.name
        click.echo(f"\n📦 Auditing {package_name}...")

        audit = {
            "name": package_name,
            "path": str(package_path),
            "python_files": 0,
            "test_files": 0,
            "total_lines": 0,
            "directories": 0,
            "modules": {},
            "size_mb": 0,
            "has_docs": False,
            "doc_files": 0,
            "largest_files": [],
        }

        # Check for docs and pyproject.toml
        docs_dir = package_path / "docs"
        if docs_dir.exists():
            audit["has_docs"] = True
            audit["doc_files"] = len(list(docs_dir.rglob("*.rst"))) + len(
                list(docs_dir.rglob("*.md"))
            )

        # Check for pyproject.toml (required by seed_intersphinx_mapping)
        pyproject_path = package_path / "pyproject.toml"
        audit["has_pyproject"] = pyproject_path.exists()

        # Find source directory
        src_dirs = []
        if (package_path / "src").exists():
            src_dirs.append(package_path / "src")
        if (package_path / package_name.replace("-", "_")).exists():
            src_dirs.append(package_path / package_name.replace("-", "_"))

        # Analyze Python files
        all_py_files = []
        for src_dir in src_dirs:
            py_files = list(src_dir.rglob("*.py"))
            all_py_files.extend(py_files)

        # Also check root level Python files
        root_py_files = list(package_path.glob("*.py"))
        all_py_files.extend(root_py_files)

        # Process files
        file_sizes = []
        for py_file in all_py_files:
            relative_path = py_file.relative_to(package_path)

            # Skip __pycache__
            if "__pycache__" in str(relative_path):
                continue

            # Count test files separately
            if "test" in py_file.name or "test" in str(relative_path):
                audit["test_files"] += 1
            else:
                audit["python_files"] += 1

            # Get file stats
            try:
                stat = py_file.stat()
                size_kb = stat.st_size / 1024
                file_sizes.append((relative_path, size_kb))

                # Count lines
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = len(f.readlines())
                    audit["total_lines"] += lines

                # Track module structure
                module_parts = relative_path.parts[:-1]  # Exclude filename
                if module_parts:
                    module_path = "/".join(module_parts)
                    if module_path not in audit["modules"]:
                        audit["modules"][module_path] = 0
                    audit["modules"][module_path] += 1

            except Exception as e:
                click.echo(f"   ⚠️  Error reading {relative_path}: {e}")

        # Calculate total size
        total_size_mb = sum(size for _, size in file_sizes) / 1024
        audit["size_mb"] = round(total_size_mb, 2)

        # Find largest files
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        audit["largest_files"] = [
            {"path": str(path), "size_kb": round(size, 1)}
            for path, size in file_sizes[:5]
        ]

        # Count directories
        all_dirs = set()
        for py_file in all_py_files:
            all_dirs.update(py_file.relative_to(package_path).parents)
        audit["directories"] = len(all_dirs)

        # Display summary
        click.echo(
            f"   📊 Files: {audit['python_files']} Python, {audit['test_files']} tests"
        )
        click.echo(f"   📏 Lines: {audit['total_lines']:,}")
        click.echo(f"   💾 Size: {audit['size_mb']} MB")
        click.echo(f"   📁 Directories: {audit['directories']}")

        # Show build readiness
        build_ready = audit["has_docs"] and audit["has_pyproject"]
        if build_ready:
            click.echo(f"   ✅ Ready for docs build (has docs/ and pyproject.toml)")
        else:
            missing = []
            if not audit["has_docs"]:
                missing.append("docs/")
            if not audit["has_pyproject"]:
                missing.append("pyproject.toml")
            click.echo(
                f"   ⚠️  Not ready for docs build (missing: {', '.join(missing)})"
            )

        return audit

    def audit_monorepo(self) -> Dict:
        """Audit all packages in a monorepo."""
        packages_dir = self.root_path / "packages"

        if not packages_dir.exists():
            click.echo("❌ No packages directory found")
            return self.audit_data

        # Find all packages
        packages = [
            p
            for p in packages_dir.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ]
        click.echo(f"\n🔍 Found {len(packages)} packages to audit")

        total_files = 0
        total_lines = 0
        total_size = 0

        # Audit each package
        for package_path in sorted(packages):
            audit = self.audit_package(package_path)
            self.audit_data["packages"][package_path.name] = audit

            total_files += audit["python_files"] + audit["test_files"]
            total_lines += audit["total_lines"]
            total_size += audit["size_mb"]

        # Summary
        self.audit_data["summary"] = {
            "total_packages": len(packages),
            "total_python_files": total_files,
            "total_lines": total_lines,
            "total_size_mb": round(total_size, 2),
            "average_files_per_package": (
                round(total_files / len(packages)) if packages else 0
            ),
            "largest_packages": self._get_largest_packages(5),
        }

        return self.audit_data

    def _get_largest_packages(self, count: int) -> List[Dict]:
        """Get the largest packages by file count."""
        packages = []
        for name, audit in self.audit_data["packages"].items():
            packages.append(
                {
                    "name": name,
                    "files": audit["python_files"],
                    "lines": audit["total_lines"],
                    "size_mb": audit["size_mb"],
                }
            )

        packages.sort(key=lambda x: x["files"], reverse=True)
        return packages[:count]

    def save_audit(self, output_path: Path):
        """Save audit results to JSON file."""
        with open(output_path, "w") as f:
            json.dump(self.audit_data, f, indent=2)
        click.echo(f"\n💾 Audit saved to: {output_path}")

    def print_summary(self):
        """Print a summary of the audit."""
        summary = self.audit_data["summary"]

        click.echo("\n" + "=" * 60)
        click.echo("📊 MONOREPO AUDIT SUMMARY")
        click.echo("=" * 60)
        click.echo(f"Total Packages:      {summary['total_packages']}")
        click.echo(f"Total Python Files:  {summary['total_python_files']:,}")
        click.echo(f"Total Lines:         {summary['total_lines']:,}")
        click.echo(f"Total Size:          {summary['total_size_mb']} MB")
        click.echo(f"Avg Files/Package:   {summary['average_files_per_package']}")

        if summary["largest_packages"]:
            click.echo("\n🏆 Largest Packages:")
            for pkg in summary["largest_packages"]:
                click.echo(
                    f"   {pkg['name']:15} {pkg['files']:4} files, {pkg['lines']:7,} lines, {pkg['size_mb']:6.1f} MB"
                )

        # Estimate build time
        total_files = summary["total_python_files"]
        est_read_time = total_files * 0.1  # ~0.1s per file for reading
        est_build_time = total_files * 0.5  # ~0.5s per file for building
        total_est = (est_read_time + est_build_time) / 60

        click.echo(f"\n⏱️  Estimated Documentation Build Time: {total_est:.1f} minutes")
        click.echo(f"   (Based on {total_files} files at ~0.6s per file)")

        # Warnings
        if total_files > 1000:
            click.echo("\n⚠️  WARNING: Large codebase detected!")
            click.echo("   - Consider building packages individually")
            click.echo("   - Use parallel builds where possible")
            click.echo("   - Monitor memory usage (may need 2-4GB)")


def audit_before_build(root_path: Path) -> Dict:
    """Run audit before starting documentation build."""
    auditor = PackageAuditor(root_path)
    audit_data = auditor.audit_monorepo()

    # Save to build monitoring directory
    monitor_dir = Path.cwd() / "build_monitoring"
    monitor_dir.mkdir(exist_ok=True)

    audit_file = monitor_dir / "pre_build_audit.json"
    auditor.save_audit(audit_file)
    auditor.print_summary()

    return audit_data


if __name__ == "__main__":
    # For testing
    import sys

    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
    else:
        root = Path.cwd()

    audit_before_build(root)
