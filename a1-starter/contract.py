"""
CSC148, Winter 2024
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
        Stores a Boolean Value which is initially False,
        This is updated to True when we reach the end date of the contract
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>. 
        This may be the first month of the contract. 
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """
    A Term Contract for a Phone Line.

    Creates the bill according to Term Contract.
    - A TermContract has a start date and an end date,
        along with that it also has a Fixed deposit, and free minutes
        refreshed every month
    - Every new month, it updates the bill with the term monthly fee,
        then sets the per minute cost for Term Contract
    - First the free minutes are used up until there are no free minutes left,
        then for duration of the call in minutes
      it adds that into the billed minutes
    -Cancel contract returns the cost of the bill using the self.bill.get_cost()

    === Public Attributes ===
    end:
         stores the end date of the Contract.
    tdr:
        Stores a Boolean Value which is initially False, This is updated to True
        when we reach the end date of the contract.

    Representation Invariants:
        - month: 13 > month > 0
        - year: range(0, 9999)
    """
    # === Private attributes ===
    # _year:
    #  stores the current year, and is updated everytime new_month(month: int,
    #  year: int, bill: Bill) is called
    # _month:
    #  stores the current month, and is updated everytime new_month(month: int,
    #  year: int, bill: Bill) is called

    end: datetime.date
    _month: int
    _year: int

    def __init__(self, start: datetime.date, end: datetime.date) -> \
            None:
        Contract.__init__(self, start)
        self.end = end
        self._month = 0
        self._year = 0

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """
        The new month instantiates the new bill,
        -It adds fixed monthly cost to the new bill,
        -If it is the start and start month it adds the term deposit, since
            the customer pays this deposit in the first
            month
        -If the new month "exceeds"  the end date,(meaning if the end date is
            passed) then the term deposit is
            subtracted from the fixed cost for the new bill, and term
            deposit is added back to the old bil
            note: in a case where the old bill does not exist,
            adding back deposit to the old bill should not execute,
            hence try-except is used
        -It sets the rates for the new bill by passing the per minute cost
            for term contract
        -It stores the bill in the instance of TermContract
        """
        bill.add_fixed_cost(TERM_MONTHLY_FEE)
        if year == self.start.year and month == self.start.month:
            bill.add_fixed_cost(TERM_DEPOSIT)
        if (year > self.end.year) or ((month > self.end.month)
                                      and (year == self.end.year)):
            result = -1 * TERM_DEPOSIT
            bill.add_fixed_cost(result)
            try:
                self.bill.add_fixed_cost(int(TERM_DEPOSIT))
            except AttributeError:
                pass
        bill.set_rates("TERM", TERM_MINS_COST)
        self.bill = bill
        self._month = month
        self._year = year

    def bill_call(self, call: Call) -> None:
        """
        The bill_call bills the call,
        - If the free minutes for that particular bills are over,
            then it adds to the billed minutes of that particular
            bill
        - Otherwise, for every minute of the call duration,
            it adds free minutes to the bill, after which it checks if
            all the free minutes are used up or not, if they are,
            then it adds the remaining minutes to the billed minute
            for that particular bill
        """
        if self.bill.free_min == TERM_MINS:
            self.bill.add_billed_minutes(ceil(call.duration / 60.0))
        else:
            for i in range(ceil(call.duration / 60.0)):
                self.bill.add_free_minutes(1)
                if self.bill.free_min == TERM_MINS:
                    (self.bill.add_billed_minutes
                     (ceil((call.duration - (i + 1)) / 60.0)))


class MTMContract(Contract):
    """
    A Month to Month Contract for a Phone Line.

    Creates the bill according to Month to Month Contract.
    - A Month to Month contract only has a start date
    - It has a fixed monthly fee, and cost per minute
    -Cancel contract returns the cost of the bill using the self.bill.get_cost()

    Representation Invariants:
        - month: 13 > month > 0
        - year: range(0, 9999)
    """

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """
        The new month instantiates the new bill,
        -It adds fixed monthly cost to the new bill,
        -It sets the rates for the new bill by passing the per minute cost for
            Month to Month Contract
        -It stores the bill in the instance of Month to Month Contract
        """
        bill.add_fixed_cost(MTM_MONTHLY_FEE)
        bill.set_rates("MTM", MTM_MINS_COST)
        self.bill = bill


class PrepaidContract(Contract):
    """
    A Term Contract for a Phone Line.

    Creates the bill according to Prepaid Contract.
    - A Prepaid contract has a start date and a balance,
    - Customer pays this balance at the start of the month
    - A negative balance means credit of that amount
    - first the balance gets used up
    -Cancel contract returns the cost of the bill using the self.bill.get_cost()

    Representation Invariants:
        - month: 13 > month > 0
        - year: range(0, 9999)
        - balance: int

    """
    # === Private attributes ===
    # _balance:
    #   stores the balance of the Contract

    _credit: float
    initial: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        Contract.__init__(self, start)
        self._credit = -1 * balance
        self.initial = 0

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """
        The new month instantiates the new bill,
        -It sets the rates for the new bill by passing the
            per minute cost for Prepaid contract
        -If the no of credit available is less than 10,
            then it adds 25 credit to the balance
        -It adds negative fixed cost(credit) to the new bill,
        -It stores the bill in the instance of TermContract
        """
        bill.set_rates("PREPAID", PREPAID_MINS_COST)
        if self.initial == 1:
            self._credit = self.bill.get_cost()
        if self._credit > -10:
            self._credit -= 25
        bill.add_fixed_cost(self._credit)
        self.initial = 1
        self.bill = bill

    def cancel_contract(self) -> float:
        """
        Return the amount owed in order to close the phone line associated
        with this contract, by fortifying the balance left on the account if any
        """
        if self.bill.get_cost() > 0:
            return self.bill.get_cost()
        return 0


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
