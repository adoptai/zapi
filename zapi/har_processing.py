"""HAR file processing and analysis module."""

import json
import os
import re
from typing import Dict, List, Any, Tuple, Optional
from urllib.parse import urlparse
from dataclasses import dataclass


@dataclass
class HarStats:
    """Statistics for a HAR file."""
    total_entries: int
    valid_entries: int
    skipped_entries: int
    unique_domains: int
    estimated_cost_usd: float
    estimated_time_minutes: float
    skipped_by_reason: Dict[str, int]
    domains: List[str]


class HarProcessingError(Exception):
    """Base exception for HAR processing errors."""
    pass


class HarProcessor:
    """
    Class to preprocess and analyze HAR files.
    
    Provides functionality to load HAR files, extract entries, and generate
    statistics including cost and time estimates for processing.
    """
    
    # Cost per entry in USD
    COST_PER_ENTRY = 0.02
    
    # Time per entry in minutes (24 seconds = 0.4 minutes)
    TIME_PER_ENTRY_MINUTES = 24 / 60
    
    # Filter patterns for static assets and non-API content
    DENY_EXTENSIONS = re.compile(
        r"\.(js|css|png|jpe?g|gif|svg|webp|ico|bmp|avif|mp4|webm|mp3|wav|woff2?|ttf|otf|map|jpf)(\?.*)?$",
        re.IGNORECASE,
    )
    
    # MIME types to exclude
    DENY_MIMETYPES = {
        "text/css",
        "text/javascript",
        "application/javascript",
        "application/x-javascript",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/x-icon",
        "font/woff",
        "font/woff2",
        "font/ttf",
        "font/otf",
        "audio/mpeg",
        "audio/wav",
        "video/mp4",
        "video/webm",
        "application/pdf",
        "application/font-woff",
    }
    
    def __init__(self, har_file_path: str):
        """
        Initialize HAR processor with a file path.
        
        Args:
            har_file_path: Path to the HAR file to process
            
        Raises:
            HarProcessingError: If file doesn't exist or is not readable
        """
        self.har_file_path = har_file_path
        self.har_data = None
        self.entries = []
        self.skipped_entries_by_reason: Dict[str, List[Dict]] = {
            "invalid_entry_format": [],
            "non_http_scheme": [],
            "missing_url": [],
            "parsing_error": [],
            "denied_extension": [],
            "denied_mime_type": []
        }
        self.skipped_counters: Dict[str, int] = {
            "invalid_entry_format": 0,
            "non_http_scheme": 0,
            "missing_url": 0,
            "parsing_error": 0,
            "denied_extension": 0,
            "denied_mime_type": 0
        }
        self.skipped_entries = 0
        self.domains_found = set()
        
        # Validate file exists and is readable
        if not os.path.exists(har_file_path):
            raise HarProcessingError(f"HAR file not found: {har_file_path}")
        
        if not os.access(har_file_path, os.R_OK):
            raise HarProcessingError(f"HAR file is not readable: {har_file_path}")
    
    def load_and_process(self) -> HarStats:
        """
        Load HAR file and process all entries to generate statistics.
        
        Returns:
            HarStats object containing comprehensive statistics
            
        Raises:
            HarProcessingError: If file processing fails
        """
        try:
            # Load HAR file content
            with open(self.har_file_path, "r", encoding="utf-8", errors='replace') as f:
                har_file_content = f.read()
            
            # Parse JSON
            try:
                self.har_data = json.loads(har_file_content)
            except json.JSONDecodeError as e:
                raise HarProcessingError(f"Invalid JSON in HAR file: {e}")
            
            # Validate HAR structure
            if not isinstance(self.har_data, dict):
                raise HarProcessingError("HAR file must contain a JSON object")
            
            if "log" not in self.har_data:
                raise HarProcessingError("HAR file missing 'log' section")
            
            if "entries" not in self.har_data["log"]:
                raise HarProcessingError("HAR file missing 'entries' in log section")
            
            entries = self.har_data["log"]["entries"]
            if not isinstance(entries, list):
                raise HarProcessingError("HAR entries must be a list")
            
            # Process each entry
            valid_entries = 0
            for entry in entries:
                if self._process_entry(entry):
                    valid_entries += 1
            
            # Generate statistics
            total_entries = len(entries)
            
            return HarStats(
                total_entries=total_entries,
                valid_entries=valid_entries,
                skipped_entries=self.skipped_entries,
                unique_domains=len(self.domains_found),
                estimated_cost_usd=valid_entries * self.COST_PER_ENTRY,
                estimated_time_minutes=valid_entries * self.TIME_PER_ENTRY_MINUTES,
                skipped_by_reason=dict(self.skipped_counters),
                domains=sorted(list(self.domains_found))
            )
            
        except FileNotFoundError:
            raise HarProcessingError(f"HAR file not found: {self.har_file_path}")
        except PermissionError:
            raise HarProcessingError(f"Permission denied reading HAR file: {self.har_file_path}")
        except Exception as e:
            raise HarProcessingError(f"Error processing HAR file: {e}")
    
    def _process_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Process a single HAR entry and extract relevant information.
        
        Args:
            entry: HAR entry dictionary
            
        Returns:
            True if entry is valid and processed, False if skipped
        """
        try:
            # Basic validation - check for required fields
            if "request" not in entry or "response" not in entry:
                self.skipped_entries_by_reason["invalid_entry_format"].append(entry)
                self.skipped_counters["invalid_entry_format"] += 1
                self.skipped_entries += 1
                return False
            
            # Extract URL
            url = self._extract_url_from_entry(entry)
            if not url:
                self.skipped_entries_by_reason["missing_url"].append(entry)
                self.skipped_counters["missing_url"] += 1
                self.skipped_entries += 1
                return False
            
            # Validate HTTP/HTTPS scheme
            if not url.lower().startswith(("http://", "https://")):
                self.skipped_entries_by_reason["non_http_scheme"].append(entry)
                self.skipped_counters["non_http_scheme"] += 1
                self.skipped_entries += 1
                return False
            
            # Filter by file extensions - exclude static assets
            try:
                parsed_url = urlparse(url)
                path = parsed_url.path
                if self.DENY_EXTENSIONS.search(path):
                    self.skipped_entries_by_reason["denied_extension"].append(entry)
                    self.skipped_counters["denied_extension"] += 1
                    self.skipped_entries += 1
                    return False
            except Exception:
                # URL parsing failed, but we'll continue processing
                pass
            
            # Filter by response MIME types
            response_content = self._extract_response_content(entry)
            mime_type = response_content.get("mimeType", "").split(";")[0]
            if mime_type in self.DENY_MIMETYPES:
                self.skipped_entries_by_reason["denied_mime_type"].append(entry)
                self.skipped_counters["denied_mime_type"] += 1
                self.skipped_entries += 1
                return False
            
            # Extract domain information
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                if domain:
                    self.domains_found.add(domain)
            except Exception:
                # URL parsing failed, but we'll still count it as valid
                pass
            
            # Store processed entry
            self.entries.append(entry)
            return True
            
        except Exception:
            self.skipped_entries_by_reason["parsing_error"].append(entry)
            self.skipped_counters["parsing_error"] += 1
            self.skipped_entries += 1
            return False
    
    def _extract_url_from_entry(self, entry: Dict[str, Any]) -> str:
        """Extract URL from an entry efficiently, returning empty string if not found."""
        try:
            return entry.get("request", {}).get("url", "")
        except (KeyError, AttributeError):
            return ""
    
    def _extract_response_content(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Extract response content from an entry efficiently, returning empty dict if not found."""
        try:
            return entry.get("response", {}).get("content", {})
        except (KeyError, AttributeError):
            return {}
    
    def save_filtered_har(self, output_path: str) -> str:
        """
        Save a new HAR file containing only the valid API-relevant entries.
        
        Args:
            output_path: Path where to save the filtered HAR file
            
        Returns:
            Path to the saved filtered HAR file
            
        Raises:
            HarProcessingError: If saving fails or no data has been processed
        """
        if self.har_data is None:
            raise HarProcessingError("No HAR data loaded. Call load_and_process() first.")
        
        if not self.entries:
            raise HarProcessingError("No valid entries found to save.")
        
        try:
            # Create a copy of the original HAR structure
            filtered_har = {
                "log": {
                    "version": self.har_data["log"].get("version", "1.2"),
                    "creator": self.har_data["log"].get("creator", {
                        "name": "ZAPI HarProcessor", 
                        "version": "1.0.0"
                    }),
                    "browser": self.har_data["log"].get("browser", {}),
                    "pages": self.har_data["log"].get("pages", []),
                    "entries": self.entries  # Only include the filtered valid entries
                }
            }
            
            # Add metadata about filtering
            if "creator" not in filtered_har["log"]:
                filtered_har["log"]["creator"] = {}
            
            filtered_har["log"]["creator"]["name"] = "ZAPI HarProcessor (Filtered)"
            filtered_har["log"]["creator"]["comment"] = f"Filtered HAR file - {len(self.entries)} API entries from {len(self.har_data['log']['entries'])} total entries"
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_har, f, indent=2, ensure_ascii=False)
            
            return output_path
            
        except (IOError, OSError) as e:
            raise HarProcessingError(f"Failed to save filtered HAR file: {e}")
        except Exception as e:
            raise HarProcessingError(f"Error creating filtered HAR file: {e}")
    
    def get_summary_report(self, stats: HarStats) -> str:
        """
        Generate a formatted summary report of the HAR analysis.
        
        Args:
            stats: HarStats object from load_and_process()
            
        Returns:
            Formatted string report
        """
        report_lines = [
            "📊 HAR File Analysis Summary",
            "=" * 50,
            f"📁 File: {os.path.basename(self.har_file_path)}",
            f"📋 Total Entries: {stats.total_entries:,}",
            f"✅ Valid Entries: {stats.valid_entries:,}",
            f"⚠️  Skipped Entries: {stats.skipped_entries:,}",
            f"🌐 Unique Domains: {stats.unique_domains:,}",
            "",
            "💰 Cost Analysis (API entries only):",
            f"   • Rate: ${self.COST_PER_ENTRY:.3f} per API entry",
            f"   • Estimated Cost: ${stats.estimated_cost_usd:.2f}",
            "",
            "⏱️  Time Estimate (API entries only):",
            f"   • Rate: {self.TIME_PER_ENTRY_MINUTES:.2f} minutes per API entry",
            f"   • Estimated Time: {stats.estimated_time_minutes:.1f} minutes",
            f"   • Estimated Time: {stats.estimated_time_minutes/60:.1f} hours",
        ]
        
        # Add skipped entry breakdown if there are any
        if stats.skipped_entries > 0:
            report_lines.extend([
                "",
                "⚠️  Skipped Entry Breakdown:"
            ])
            for reason, count in stats.skipped_by_reason.items():
                if count > 0:
                    reason_display = reason.replace('_', ' ').title()
                    report_lines.append(f"   • {reason_display}: {count:,}")
        
        # Add top domains if there are any
        if stats.domains:
            report_lines.extend([
                "",
                "🌐 Top Domains Found:"
            ])
            # Show first 10 domains
            for domain in stats.domains[:10]:
                report_lines.append(f"   • {domain}")
            
            if len(stats.domains) > 10:
                report_lines.append(f"   • ... and {len(stats.domains) - 10} more")
        
        return "\n".join(report_lines)


def analyze_har_file(har_file_path: str, save_filtered: bool = False, filtered_output_path: str = None) -> Tuple[HarStats, str, Optional[str]]:
    """
    Convenience function to analyze a HAR file and optionally save filtered version.
    
    Args:
        har_file_path: Path to the HAR file
        save_filtered: Whether to save a filtered HAR file with only API entries
        filtered_output_path: Path for filtered HAR file (auto-generated if None)
        
    Returns:
        Tuple of (HarStats, formatted_report_string, filtered_file_path_or_none)
        
    Raises:
        HarProcessingError: If processing fails
    """
    processor = HarProcessor(har_file_path)
    stats = processor.load_and_process()
    report = processor.get_summary_report(stats)
    
    filtered_file_path = None
    if save_filtered and stats.valid_entries > 0:
        if filtered_output_path is None:
            # Auto-generate filtered file name
            base_name = os.path.splitext(har_file_path)[0]
            filtered_output_path = f"{base_name}_filtered.har"
        
        filtered_file_path = processor.save_filtered_har(filtered_output_path)
    
    return stats, report, filtered_file_path
