"""
Bills and Payment API Client
Handles billing and payment operations for UMAT students
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_client import BaseAPIClient, APIResponse
from ...utils.utils.logger import get_logger


class BillsPaymentAPI(BaseAPIClient):
    """Bills and Payment API client for UMAT student portal"""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        self.logger = get_logger(self.__class__.__name__)

        # Bills and payment endpoints
        self.endpoints = {
            'get_bill_summary': '/api/Transaction/GetBillSummary',
            'get_student_bills': '/api/Bills/GetSingleStudentBill',
            'get_student_transactions': '/api/Transaction/GetStudentTransactions'
        }

    def get_bill_summary(self) -> APIResponse:
        """
        Get bill summary for the authenticated student

        Returns:
            APIResponse containing bill summary data
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='GET',
                request_url=self._build_url(self.endpoints['get_bill_summary'])
            )

        self.logger.info("Fetching student bill summary")
        response = self.get(self.endpoints['get_bill_summary'])

        if response.is_success:
            self.logger.info("Student bill summary retrieved successfully")
        else:
            self.logger.error(f"Failed to retrieve student bill summary: {response.status_code}")

        return response

    def get_student_bills(self) -> APIResponse:
        """
        Get detailed student bills for the authenticated student

        Returns:
            APIResponse containing detailed bill data
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='GET',
                request_url=self._build_url(self.endpoints['get_student_bills'])
            )

        self.logger.info("Fetching detailed student bills")
        response = self.get(self.endpoints['get_student_bills'])

        if response.is_success:
            self.logger.info("Detailed student bills retrieved successfully")
        else:
            self.logger.error(f"Failed to retrieve detailed student bills: {response.status_code}")

        return response

    def get_student_transactions(self) -> APIResponse:
        """
        Get student payment transactions for the authenticated student

        Returns:
            APIResponse containing transaction history data
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='GET',
                request_url=self._build_url(self.endpoints['get_student_transactions'])
            )

        self.logger.info("Fetching student payment transactions")
        response = self.get(self.endpoints['get_student_transactions'])

        if response.is_success:
            self.logger.info("Student payment transactions retrieved successfully")
        else:
            self.logger.error(f"Failed to retrieve student payment transactions: {response.status_code}")

        return response

    def parse_bill_summary(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse bill summary response data into a clean format

        Args:
            response_data: Raw API response data

        Returns:
            Dictionary containing parsed bill summary
        """
        if not response_data:
            return {}

        # Clean up currency formatting
        def clean_amount(amount_str: str) -> float:
            if not amount_str:
                return 0.0
            # Remove currency symbols, commas, and parentheses
            cleaned = str(amount_str).replace(',', '').replace('(', '').replace(')', '')
            try:
                return float(cleaned)
            except (ValueError, TypeError):
                return 0.0

        summary = {
            'current_bill': clean_amount(response_data.get('currentBill', '0')),
            'previous_balance': clean_amount(response_data.get('previousBalance', '0')),
            'total_current_bill': clean_amount(response_data.get('totalCurrentBill', '0')),
            'amount_paid': clean_amount(response_data.get('amountPaid', '0')),
            'refund': clean_amount(response_data.get('refund', '0')),
            'outstanding_balance': clean_amount(response_data.get('outstandingBalance', '0')),
            'check_balance': response_data.get('checkBalance', 0.0),
            'has_current_scholarship_package': response_data.get('hasCurrentScholarshipPackage', False),
            'is_huge_balance_over_50_percent': response_data.get('isHugeBalanceOver50Percent', False),
            'is_payment_over_50_percent': response_data.get('isPaymentOver50Percent', False),
            'overall_bill_total': clean_amount(response_data.get('overAllBillTotal', '0')),
            'payment_allowed': clean_amount(response_data.get('paymentAllowed', '0')),
            'currency': response_data.get('currency', 'GHS')
        }

        return summary

    def parse_student_bills(self, response_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse student bills response data into a clean format

        Args:
            response_data: Raw API response data (list of bills)

        Returns:
            List of parsed bill data
        """
        if not response_data:
            return []

        bills = []
        for bill_data in response_data:
            # Clean up amount formatting
            def clean_amount(amount_str: str) -> float:
                if not amount_str:
                    return 0.0
                cleaned = str(amount_str).replace(',', '').replace('(', '').replace(')', '')
                # Handle negative amounts in parentheses
                if '(' in str(amount_str) and ')' in str(amount_str):
                    cleaned = '-' + cleaned
                try:
                    return float(cleaned)
                except (ValueError, TypeError):
                    return 0.0

            bill = {
                'id': bill_data.get('id'),
                'student_number': bill_data.get('studentNumber'),
                'billing_item_id': bill_data.get('billingItemId', 0),
                'amount': clean_amount(bill_data.get('amount', '0')),
                'total_amount': clean_amount(bill_data.get('totalAmount', '0')),
                'billing_date': bill_data.get('billingDate', ''),
                'academic_period': {},
                'compositions': []
            }

            # Parse academic period
            academic_period = bill_data.get('academicPeriod', {})
            if academic_period:
                bill['academic_period'] = {
                    'lower_year': academic_period.get('lowerYear', 0),
                    'upper_year': academic_period.get('upperYear', 0),
                    'academic_year': academic_period.get('academicYear', 'N/A'),
                    'semester': academic_period.get('semester', 0)
                }

            # Parse bill compositions (fee breakdown)
            compositions = bill_data.get('compositions', [])
            for comp in compositions:
                composition = {
                    'item': comp.get('compItem', 'N/A'),
                    'amount': clean_amount(comp.get('compAmount', '0'))
                }
                bill['compositions'].append(composition)

            bills.append(bill)

        return bills

    def parse_student_transactions(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse student transactions response data into a clean format

        Args:
            response_data: Raw API response data

        Returns:
            Dictionary containing parsed transaction data
        """
        if not response_data:
            return {'school_fees': [], 'other_fees': []}

        def clean_amount(amount_str: str) -> float:
            if not amount_str:
                return 0.0
            cleaned = str(amount_str).replace(',', '')
            try:
                return float(cleaned)
            except (ValueError, TypeError):
                return 0.0

        def parse_date(date_str: str) -> str:
            if not date_str:
                return 'N/A'
            try:
                # Parse ISO format date
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                return date_str

        # Parse school fees transactions
        school_fees = []
        for transaction in response_data.get('schoolFees', []):
            fee = {
                'id': transaction.get('id'),
                'amount': clean_amount(transaction.get('amount', '0')),
                'year': transaction.get('year', 0),
                'academic_year': transaction.get('academicYear', 'N/A'),
                'semester': transaction.get('semester', 0),
                'payment_date': parse_date(transaction.get('paymentDate', '')),
                'transaction_type': transaction.get('transactionType', 0),
                'narration': transaction.get('naration', 'N/A'),  # Note: API uses 'naration' (typo)
                'payment_id': transaction.get('paymentId', 'N/A'),
                'transaction_status': transaction.get('transactionStatus', 0),
                'receipt_no': transaction.get('receiptNo', 'N/A')
            }
            school_fees.append(fee)

        # Parse other fees transactions
        other_fees = []
        for transaction in response_data.get('otherFees', []):
            fee = {
                'id': transaction.get('id'),
                'amount': clean_amount(transaction.get('amount', '0')),
                'year': transaction.get('year', 0),
                'academic_year': transaction.get('academicYear', 'N/A'),
                'semester': transaction.get('semester', 0),
                'payment_date': parse_date(transaction.get('paymentDate', '')),
                'transaction_type': transaction.get('transactionType', 0),
                'narration': transaction.get('naration', 'N/A'),
                'payment_id': transaction.get('paymentId', 'N/A'),
                'transaction_status': transaction.get('transactionStatus', 0),
                'receipt_no': transaction.get('receiptNo', 'N/A')
            }
            other_fees.append(fee)

        return {
            'school_fees': school_fees,
            'other_fees': other_fees
        }

    def get_payment_summary(self, bill_summary: Dict[str, Any], transactions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive payment summary

        Args:
            bill_summary: Parsed bill summary data
            transactions: Parsed transaction data

        Returns:
            Dictionary containing payment summary metrics
        """
        if not bill_summary and not transactions:
            return {
                'total_bills': 0.0,
                'total_payments': 0.0,
                'outstanding_balance': 0.0,
                'payment_status': 'Unknown',
                'total_transactions': 0,
                'latest_payment': 'N/A',
                'payment_methods': []
            }

        # Calculate totals from transactions
        school_fees = transactions.get('school_fees', [])
        other_fees = transactions.get('other_fees', [])

        total_school_fee_payments = sum(fee.get('amount', 0) for fee in school_fees)
        total_other_fee_payments = sum(fee.get('amount', 0) for fee in other_fees)
        total_payments = total_school_fee_payments + total_other_fee_payments

        # Get latest payment
        all_transactions = school_fees + other_fees
        latest_payment = 'N/A'
        if all_transactions:
            # Sort by payment date (most recent first)
            sorted_transactions = sorted(all_transactions,
                                       key=lambda x: x.get('payment_date', ''),
                                       reverse=True)
            if sorted_transactions:
                latest_payment = sorted_transactions[0].get('payment_date', 'N/A')

        # Extract payment methods
        payment_methods = []
        for transaction in all_transactions:
            narration = transaction.get('narration', '')
            if narration and narration != 'N/A':
                if narration not in payment_methods:
                    payment_methods.append(narration)

        # Determine payment status
        outstanding = bill_summary.get('outstanding_balance', 0.0)
        if outstanding <= 0:
            payment_status = 'Paid'
        elif outstanding > 0:
            payment_status = 'Outstanding'
        else:
            payment_status = 'Overpaid'

        return {
            'total_bills': bill_summary.get('overall_bill_total', 0.0),
            'total_payments': total_payments,
            'outstanding_balance': outstanding,
            'payment_status': payment_status,
            'total_transactions': len(all_transactions),
            'latest_payment': latest_payment,
            'payment_methods': payment_methods,
            'currency': bill_summary.get('currency', 'GHS'),
            'has_scholarship': bill_summary.get('has_current_scholarship_package', False),
            'school_fee_payments': total_school_fee_payments,
            'other_fee_payments': total_other_fee_payments
        }