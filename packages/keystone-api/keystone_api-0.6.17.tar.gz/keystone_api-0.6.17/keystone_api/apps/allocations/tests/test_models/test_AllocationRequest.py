"""Unit tests for the `AllocationRequest` class."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.allocations.models import AllocationRequest
from apps.users.models import Team, User


class CleanMethod(TestCase):
    """Test the validation of record data via the `clean` method."""

    def setUp(self) -> None:
        """Create mock user records"""

        self.user = User.objects.create_user(username='pi', password='foobar123!')
        self.team = Team.objects.create(name='Test Team')

    def test_clean_method_valid(self) -> None:
        """Verify the clean method returns successfully when dates are valid."""

        allocation_request = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            team=self.team,
            active='2024-01-01',
            expire='2024-12-31'
        )

        allocation_request.clean()

    def test_clean_method_invalid(self) -> None:
        """Verify the clean method raises a `ValidationError` when active date is after or equal to expire."""

        allocation_request_after = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            team=self.team,
            active='2024-12-31',
            expire='2024-01-01'
        )

        with self.assertRaises(ValidationError):
            allocation_request_after.clean()

        allocation_request_equal = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            team=self.team,
            active='2024-01-01',
            expire='2024-01-01'
        )

        with self.assertRaises(ValidationError):
            allocation_request_equal.clean()


class GetTeamMethod(TestCase):
    """Test the retrieval of a request's parent team via the `get_team` method."""

    def setUp(self) -> None:
        """Create mock user records"""

        self.user = User.objects.create_user(username='pi', password='foobar123!')
        self.team = Team.objects.create(name='Test Team')
        self.allocation_request = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            team=self.team
        )

    def test_get_team(self) -> None:
        """Verify the `get_team` method returns the correct `Team` instance."""

        self.assertEqual(self.team, self.allocation_request.get_team())
