#!/usr/bin/env python3
"""
UMAT Student Reference Number Generator - Fixed Version
Generate valid UMAT student reference numbers based on identified pattern
"""

import random
import json
import os
from datetime import datetime
from typing import List, Set

class UMATReferenceGenerator:
    """Generate UMAT student reference numbers"""

    def __init__(self):
        # Pattern analysis from valid references
        self.institution_code = "9012"  # First 4 digits (constant)
        self.year_suffix = "22"         # Last 2 digits (for 2022)
        self.sequence_length = 4        # Middle 4 digits (variable)

        # Known valid references for validation
        self.known_valid = {
            "9012562822",
            "9012281822"
        }

        # Store generated numbers to avoid duplicates
        self.generated_numbers: Set[str] = set()

        self._display_banner()

    def _display_banner(self):
        """Display generator banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║           UMAT REFERENCE NUMBER GENERATOR v2.0              ║
║                                                              ║
║  🎯 Pattern: 9012XXXX22                                     ║
║  📊 Institution Code: 9012                                  ║
║  📅 Year: 2022 (suffix: 22)                                ║
║  🔢 Variable: 4-digit sequence (positions 5-8)             ║
║  📝 Total Length: 10 digits                                 ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def generate_sequence_number(self, method: str = "random") -> str:
        """Generate 4-digit sequence number"""
        if method == "random":
            # Generate random 4-digit number
            return f"{random.randint(1000, 9999):04d}"
        elif method == "sequential":
            # Generate sequential numbers starting from known patterns
            # Extract sequence numbers from known valid references
            known_sequences = []
            for ref in self.known_valid:
                seq = ref[4:8]  # Extract middle 4 digits
                known_sequences.append(int(seq))

            # Start from max known sequence + 1
            if known_sequences:
                next_seq = max(known_sequences) + len(self.generated_numbers) + 1
            else:
                next_seq = 1000 + len(self.generated_numbers)

            return f"{next_seq:04d}"
        elif method == "pattern_based":
            # Generate based on patterns observed in valid references
            # Known sequences: 5628, 2818
            # Try to follow similar patterns
            patterns = [
                lambda: f"{random.randint(20, 60)}{random.randint(10, 99)}",
                lambda: f"{random.randint(10, 99)}{random.randint(10, 99)}",
                lambda: f"{random.choice([2, 3, 4, 5, 6])}{random.randint(100, 999)}",
            ]
            return random.choice(patterns)()

    def generate_reference_number(self, method: str = "random") -> str:
        """Generate a complete UMAT reference number"""
        sequence = self.generate_sequence_number(method)
        reference = f"{self.institution_code}{sequence}{self.year_suffix}"
        return reference

    def generate_multiple_references(self, count: int, method: str = "random",
                                   avoid_duplicates: bool = True) -> List[str]:
        """Generate multiple UMAT reference numbers"""
        references = []
        attempts = 0
        max_attempts = count * 10  # Prevent infinite loops

        print(f"\n🔄 Generating {count} UMAT reference numbers using '{method}' method...")

        while len(references) < count and attempts < max_attempts:
            ref = self.generate_reference_number(method)

            if avoid_duplicates:
                if ref not in self.generated_numbers and ref not in references:
                    references.append(ref)
                    self.generated_numbers.add(ref)
            else:
                references.append(ref)

            attempts += 1

        if len(references) < count:
            print(f"⚠️ Warning: Only generated {len(references)} unique numbers out of {count} requested")

        return references

    def validate_reference_format(self, reference: str) -> bool:
        """Validate if a reference number follows the correct format"""
        if len(reference) != 10:
            return False

        if not reference.isdigit():
            return False

        if not reference.startswith(self.institution_code):
            return False

        if not reference.endswith(self.year_suffix):
            return False

        return True

    def analyze_generated_references(self, references: List[str]) -> dict:
        """Analyze the generated reference numbers"""
        analysis = {
            'total_generated': len(references),
            'valid_format': 0,
            'unique_sequences': set(),
            'sequence_range': {'min': None, 'max': None},
            'duplicates': 0,
            'sample_references': references[:10]
        }

        sequences = []
        for ref in references:
            if self.validate_reference_format(ref):
                analysis['valid_format'] += 1
                sequence = ref[4:8]
                analysis['unique_sequences'].add(sequence)
                sequences.append(int(sequence))

        if sequences:
            analysis['sequence_range']['min'] = min(sequences)
            analysis['sequence_range']['max'] = max(sequences)

        analysis['duplicates'] = len(references) - len(set(references))
        analysis['unique_sequences'] = len(analysis['unique_sequences'])

        return analysis

    def save_references_to_file(self, references: List[str], filename: str = None) -> str:
        """Save generated references to a file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"umat_references_{timestamp}.json"

        # Ensure we're saving in the current directory
        full_path = os.path.abspath(filename)

        data = {
            'generation_timestamp': datetime.now().isoformat(),
            'pattern_info': {
                'institution_code': self.institution_code,
                'year_suffix': self.year_suffix,
                'total_length': 10,
                'format': f"{self.institution_code}XXXX{self.year_suffix}"
            },
            'known_valid_references': list(self.known_valid),
            'generated_references': references,
            'analysis': self.analyze_generated_references(references)
        }

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 References saved to: {full_path}")
            return full_path
        except Exception as e:
            print(f"❌ Error saving file: {str(e)}")
            return None

    def save_references_to_txt(self, references: List[str], filename: str = None) -> str:
        """Save generated references to a simple text file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"umat_references_{timestamp}.txt"

        # Ensure we're saving in the current directory
        full_path = os.path.abspath(filename)

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write("UMAT Student Reference Numbers\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Pattern: {self.institution_code}XXXX{self.year_suffix}\n")
                f.write(f"Total: {len(references)}\n")
                f.write("=" * 50 + "\n\n")

                for i, ref in enumerate(references, 1):
                    f.write(f"{i:3d}. {ref}\n")

                f.write("\n" + "=" * 50 + "\n")
                f.write("Known Valid References:\n")
                for i, ref in enumerate(self.known_valid, 1):
                    f.write(f"{i}. {ref}\n")

            print(f"📄 References saved to text file: {full_path}")
            return full_path
        except Exception as e:
            print(f"❌ Error saving text file: {str(e)}")
            return None

    def display_references(self, references: List[str], show_analysis: bool = True):
        """Display generated references with analysis"""
        print(f"\n📋 Generated {len(references)} UMAT Reference Numbers:")
        print("=" * 60)

        # Display references in columns
        for i, ref in enumerate(references, 1):
            if i % 5 == 1:
                print()  # New line every 5 references
            print(f"{i:3d}. {ref}", end="  ")

        print("\n")

        if show_analysis:
            analysis = self.analyze_generated_references(references)
            print("\n📊 GENERATION ANALYSIS:")
            print("=" * 40)
            print(f"Total generated: {analysis['total_generated']}")
            print(f"Valid format: {analysis['valid_format']}")
            print(f"Unique sequences: {analysis['unique_sequences']}")
            if analysis['sequence_range']['min'] is not None:
                print(f"Sequence range: {analysis['sequence_range']['min']} - {analysis['sequence_range']['max']}")
            print(f"Duplicates: {analysis['duplicates']}")

            print(f"\n🔍 Sample references:")
            for i, ref in enumerate(analysis['sample_references'][:5], 1):
                print(f"  {i}. {ref} (sequence: {ref[4:8]})")

def main():
    """Main function with interactive interface"""
    generator = UMATReferenceGenerator()

    print("🎯 UMAT Reference Number Generator")
    print("Based on pattern analysis of valid references")

    try:
        # Get user input for number of references to generate
        while True:
            try:
                count_input = input(f"\n📝 How many reference numbers to generate? (default: 100): ").strip()
                if not count_input:
                    count = 100
                else:
                    count = int(count_input)

                if count <= 0:
                    print("❌ Please enter a positive number")
                    continue
                elif count > 10000:
                    print("⚠️ Large number requested. This might take a while...")

                break
            except ValueError:
                print("❌ Please enter a valid number")

        # Get generation method
        print(f"\n🔧 Generation methods:")
        print("1. random - Random 4-digit sequences")
        print("2. sequential - Sequential from known patterns")
        print("3. pattern_based - Based on observed patterns")

        method_choice = input("Select method (1-3, default: 1): ").strip()
        method_map = {'1': 'random', '2': 'sequential', '3': 'pattern_based'}
        method = method_map.get(method_choice, 'random')

        print(f"\n🚀 Generating {count} references using '{method}' method...")

        # Generate references
        references = generator.generate_multiple_references(count, method)

        # Display results
        generator.display_references(references)

        # Save to files
        save_choice = input(f"\n💾 Save references to files? (y/n, default: y): ").strip().lower()
        if save_choice != 'n':
            # Save JSON file
            json_file = generator.save_references_to_file(references)
            # Save TXT file
            txt_file = generator.save_references_to_txt(references)

            if json_file and txt_file:
                print(f"✅ Successfully saved {len(references)} references to both JSON and TXT files")

        # Show known valid references for comparison
        print(f"\n🔍 Known valid references for comparison:")
        for i, ref in enumerate(generator.known_valid, 1):
            print(f"  {i}. {ref} (sequence: {ref[4:8]})")

        print(f"\n✅ Generation completed successfully!")

    except KeyboardInterrupt:
        print(f"\n⚠️ Generation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()