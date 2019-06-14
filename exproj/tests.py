from django.test import TestCase
from exapp import models


class Tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company = models.Company(name='mycomp')
        cls.company.save()

    def setUp(self):
        models.signal_log.clear()

    def test_1to1_forward_direct_assignment_obviously_fires(self):
        customer = models.Customer(name='1to1 forward test', company=self.company)
        customer.save()

        models.signal_log.clear()

        extra = models.CustomerExtraJunk()
        extra.customer = customer
        extra.save()

        self.assertEqual(models.signal_log.keys(), ['extra junk presave'])

    def test_1to1_forward_direct_assignment_not_allowed_if_child_unsaved(self):
        customer = models.Customer(name='1to1 unsaved forward test', company=self.company)
        extra = models.CustomerExtraJunk()
        extra.customer = customer
        with self.assertRaises(ValueError):
            extra.save()

    def test_1to1_reverse_direct_assignment_does_not_fire(self):
        customer = models.Customer(name='1to1 reverse test', company=self.company)
        customer.save()

        extra = models.CustomerExtraJunk()
        extra.save()

        models.signal_log.clear()

        customer.extrajunk = extra
        customer.save()

        self.assertIn('customer presave', models.signal_log.keys())
        # Passes on both 1.8 and 1.9
        self.assertNotIn('extra junk presave', models.signal_log.keys())

    def test_1to1_reverse_direct_assignment_if_child_unsaved(self):
        customer = models.Customer(name='1to1 unsaved forward test', company=self.company)
        customer.save()
        extra = models.CustomerExtraJunk()  # NOT saving yet
        customer.extrajunk = extra
        customer.save()  # This is allowed even though extra not saved!

        self.assertEqual(extra.customer, customer)
        # 'extra presave' not sent because extra isn't actually saved yet
        self.assertEqual(sorted(models.signal_log.keys()), ['customer presave'])

        # reloading customer proves we didn't actually save the relationship yet
        customer = models.Customer.objects.get(pk=customer.pk)
        with self.assertRaises(Exception):
            customer.extrajunk

        # saving extra does the trick
        extra.save()
        customer = models.Customer.objects.get(pk=customer.pk)
        self.assertEqual(customer.extrajunk, extra)
        self.assertEqual(
            sorted(models.signal_log.keys()), ['customer presave', 'extra junk presave'])

    def test_1toM_forward_direct_assignment_does_not_fire_related_presave(self):
        customer = models.Customer(name='1to1 cust')

        customer.company = self.company
        customer.save()

        # No save triggered on company
        self.assertEqual(len(models.signal_log['customer presave']), 1)
        self.assertItemsEqual(models.signal_log.keys(), ['customer presave'])

    def test_1toM_reverse_direct_assignment_does_not_fire_related_presave(self):
        customer2 = models.Customer(name="unsaved 1to1 cust")
        customer2.save()
        company = self.company
        self.assertItemsEqual(company.customers.all(), [])

        models.signal_log.clear()
        self.assertEqual(models.signal_log.items(), [])

        company.customers = [customer2]
        company.save()
        self.assertIn('company presave', models.signal_log.keys())

        # Save triggered on customer2 on django 1.8 but FAILS on django 1.9
        self.assertIn('customer presave', models.signal_log.keys())

        logged = models.signal_log['customer presave'][0]
        self.assertEqual(logged[0], models.Customer)
        self.assertEqual(logged[1]['instance'], customer2)

    def test_m2m_indirect_cannot_set_attr_directly(self):
        company = self.company
        customer = models.Customer(name='testing m2m forward', company=company)
        customer.save()
        cat1 = models.CustomerCategory(name='m2m cat 1')
        cat1.save()
        cat2 = models.CustomerCategory(name='m2m cat 2')
        cat2.save()

        models.signal_log.clear()

        with self.assertRaises(AttributeError):
            # TIL you can't do this if there's a `through` model.
            customer.categories_indirect = [cat1, cat2]

        with self.assertRaises(AttributeError):
            # TIL you can't do this if there's a `through` model.
            cat1.customers_indirect = [customer]

    def test_m2m_indirect_forward_fires_through_presave_but_not_rel_presave(self):
        company = self.company
        customer = models.Customer(name='testing m2m forward', company=company)
        customer.save()
        cat1 = models.CustomerCategory(name='m2m cat 1')
        cat1.save()
        cat2 = models.CustomerCategory(name='m2m cat 2')
        cat2.save()

        models.signal_log.clear()

        rel = models.CustomerCategoryRel(customer=customer, category=cat1)
        rel.save()

        # The 'through' model gets a presave, but not the related model (categories)
        self.assertEqual(models.signal_log.keys(), ['rel presave'])

    def test_m2m_direct_forward_does_not_fire_related_presave(self):
        company = self.company
        customer = models.Customer(name='testing m2m direct forward', company=company)
        customer.save()
        cat1 = models.CustomerCategory(name='m2m cat 1')
        cat1.save()
        cat2 = models.CustomerCategory(name='m2m cat 2')
        cat2.save()

        models.signal_log.clear()

        customer.categories_direct = [cat1, cat2]
        customer.save()

        # The related model (categories) don't get presave
        self.assertEqual(models.signal_log.keys(), ['customer presave'])

    def test_m2m_direct_reverse_does_not_fire_related_presave(self):
        company = self.company
        customer = models.Customer(name='testing m2m direct reverse', company=company)
        customer.save()
        cat1 = models.CustomerCategory(name='m2m cat 1')
        cat1.save()
        cat2 = models.CustomerCategory(name='m2m cat 2')
        cat2.save()

        models.signal_log.clear()

        cat1.customers_direct = [customer]
        cat2.customers_direct = [customer]
        cat1.save()
        cat2.save()

        # The customer is not saved.
        self.assertEqual(models.signal_log.keys(), ['category presave'])

    def test_m2m_direct_forward_does_not_fire_related_presave(self):
        company = self.company
        customer = models.Customer(name='testing m2m direct forward', company=company)
        customer.save()
        cat1 = models.CustomerCategory(name='m2m cat 1')
        cat1.save()
        cat2 = models.CustomerCategory(name='m2m cat 2')
        cat2.save()

        models.signal_log.clear()

        customer.categories_direct = [cat1, cat2]
        customer.save()

        # The related model (categories) don't get presave
        self.assertEqual(models.signal_log.keys(), ['customer presave'])
