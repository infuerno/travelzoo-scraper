# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists
from models import Deals, DealStats, db_connect, create_deals_table
from datetime import datetime

class TravelZooPipeline(object):
    """TravelZoo pipeline for storing scraped items in the database"""
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_deals_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save deals in the database.

        This method is called for every item pipeline component.

        """

        session = self.Session()
        datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if item.has_key('bought'):
            deal_stats = DealStats()
            deal_stats.deal_id = item['id']
            deal_stats.bought = item['bought']
            deal_stats.created_at = datetime_now
            query = session.query(DealStats).filter(DealStats.deal_id == item['id'], DealStats.replaced_at == None)
            if query.count(): # found existing stats for this deal
                existing_deal_stats = query.one()
                if existing_deal_stats.bought != item['bought']: # only replace if different
                    existing_deal_stats.replaced_at = datetime_now
                    deal_stats.original_id = existing_deal_stats.original_id if existing_deal_stats.original_id else existing_deal_stats.id
                    session.add(deal_stats)
                # else: # found an existing one, but with the same value for bought
            else:
                session.add(deal_stats)
            item.pop('bought') # causes an error when trying to map to Deals since Deals doesn't have 'bought' attribute

        deal = Deals(**item)
        deal.updated_at = datetime_now

        try:
            if session.query(exists().where(Deals.id == deal.id)).scalar():
                session.merge(deal)
            else:
                deal.created_at = datetime_now
                session.add(deal)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item

