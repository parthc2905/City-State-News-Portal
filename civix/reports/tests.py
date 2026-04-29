from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import ForeignKey, TextField
from reports.models import CitizenReport, CommentReport, AdReport
from news.models import Comment
from ads.models import Advertisement

class ReportModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User(username='test_user')

    # --- CitizenReport Tests ---
    
    def test_tc1_citizen_report_default_status(self):
        # Test Case 1: Verify CitizenReport default status
        report = CitizenReport(user=self.user, title='Fake News', reason='Contains false information.')
        self.assertEqual(report.status, 'pending')

    def test_tc2_citizen_report_str(self):
        # Test Case 2: Verify CitizenReport string representation
        report = CitizenReport(user=self.user, title='Spam Content', reason='This is spam.')
        self.assertEqual(str(report), 'Spam Content')

    def test_tc3_citizen_report_title_max_length(self):
        # Test Case 3: Verify CitizenReport title max length
        max_length = CitizenReport._meta.get_field('title').max_length
        self.assertEqual(max_length, 255)

    def test_tc4_citizen_report_article_null(self):
        # Test Case 4: Verify CitizenReport article can be null
        null_status = CitizenReport._meta.get_field('article').null
        self.assertTrue(null_status)

    def test_tc5_citizen_report_article_blank(self):
        # Test Case 5: Verify CitizenReport article can be blank
        blank_status = CitizenReport._meta.get_field('article').blank
        self.assertTrue(blank_status)

    def test_tc6_citizen_report_status_choices(self):
        # Test Case 6: Verify CitizenReport status choices
        choices = CitizenReport._meta.get_field('status').choices
        expected_choices = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
        self.assertEqual(choices, expected_choices)

    def test_tc7_citizen_report_db_table(self):
        # Test Case 7: Verify CitizenReport database table name
        self.assertEqual(CitizenReport._meta.db_table, 'citizen_report')

    def test_tc8_citizen_report_created_at_property(self):
        # Test Case 8: Verify CitizenReport created_at property
        auto_now_add = CitizenReport._meta.get_field('created_at').auto_now_add
        self.assertTrue(auto_now_add)

    def test_tc9_citizen_report_user_fk(self):
        # Test Case 9: Verify CitizenReport user relationship
        field = CitizenReport._meta.get_field('user')
        self.assertIsInstance(field, ForeignKey)

    def test_tc10_citizen_report_state_fk(self):
        # Test Case 10: Verify CitizenReport state relationship
        field = CitizenReport._meta.get_field('state')
        self.assertIsInstance(field, ForeignKey)

    def test_tc11_citizen_report_city_fk(self):
        # Test Case 11: Verify CitizenReport city relationship
        field = CitizenReport._meta.get_field('city')
        self.assertIsInstance(field, ForeignKey)


    # --- CommentReport Tests ---

    def test_tc12_comment_report_str(self):
        # Test Case 12: Verify CommentReport string representation
        comment = Comment(id=101)
        report = CommentReport(user=self.user, comment=comment, reason='Inappropriate language.')
        self.assertEqual(str(report), 'Report on Comment 101 by test_user')

    def test_tc13_comment_report_db_table(self):
        # Test Case 13: Verify CommentReport database table name
        self.assertEqual(CommentReport._meta.db_table, 'comment_report')

    def test_tc14_comment_report_reason_type(self):
        # Test Case 14: Verify CommentReport reason field type
        field = CommentReport._meta.get_field('reason')
        self.assertIsInstance(field, TextField)

    def test_tc15_comment_report_created_at_property(self):
        # Test Case 15: Verify CommentReport created_at property
        auto_now_add = CommentReport._meta.get_field('created_at').auto_now_add
        self.assertTrue(auto_now_add)

    def test_tc16_comment_report_user_fk(self):
        # Test Case 16: Verify CommentReport user relationship
        field = CommentReport._meta.get_field('user')
        self.assertIsInstance(field, ForeignKey)

    def test_tc17_comment_report_comment_fk(self):
        # Test Case 17: Verify CommentReport comment relationship
        field = CommentReport._meta.get_field('comment')
        self.assertIsInstance(field, ForeignKey)


    # --- AdReport Tests ---

    def test_tc18_ad_report_str(self):
        # Test Case 18: Verify AdReport string representation
        ad = Advertisement(id=55)
        report = AdReport(user=self.user, ad=ad, reason='Misleading ad.')
        self.assertEqual(str(report), 'Report on Ad 55 by test_user')

    def test_tc19_ad_report_db_table(self):
        # Test Case 19: Verify AdReport database table name
        self.assertEqual(AdReport._meta.db_table, 'ad_report')

    def test_tc20_ad_report_created_at_property(self):
        # Test Case 20: Verify AdReport created_at property
        auto_now_add = AdReport._meta.get_field('created_at').auto_now_add
        self.assertTrue(auto_now_add)

    def test_tc21_ad_report_ad_fk(self):
        # Test Case 21: Verify AdReport ad relationship
        field = AdReport._meta.get_field('ad')
        self.assertIsInstance(field, ForeignKey)
