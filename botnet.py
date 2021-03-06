#!/usr/bin/python2.7
# -*- coding: utf-8

from utils import Utils

import json
import logging
logger = logging.getLogger(__name__)


class Botnet:
    ut = Utils()

    def __init__(self, player):
        self.username = player.username
        self.password = player.password
        self.uhash = player.uhash
        self.botNetServers = 3
        self.botnet = []
        self.p = player
        self._initbot()

    def _initbot(self):
        """
        Grab the amount of bots in the botnet
        and populate and array of Bot class
        :return: none
        """
        data = self._botnetInfo()
        bots = json.loads(data)
        self.botnet = []
        if int(bots['count']) > 0:
            for i in bots['data']:
                bot = Bot(i['bID'], i['bLVL'], i['bPRICE'], self.username, self.password, self.uhash)
                self.botnet.append(bot)

    def printbots(self):
        """
        Print a list of player PCs in the botnet
        :return: None
        """
        for bot in self.botnet:
            logger.info(bot)

    def getbotnetdata(self):
        """
        Return an array of bot class.
        Contains all the bots in the botnet.
        :return: list of bot class
        """
        return self.botnet

    def getInfo(self):
        """
        Get info about the entire botnet.
        Including if you can attack bot net servers etc.
        Also botnet PC info.
        :return: list of vHack serves that can be hacked.
                 ['1','2','1']. '1' = can be hacked, '2' time not elapsed.
        """
        response = self.ut.requestString(self.username, self.password, self.uhash, "vh_botnetInfo.php")
        response = json.loads(response)
        l = []
        l.append(str(response['canAtt1']))
        l.append(str(response['canAtt2']))
        l.append(str(response['canAtt3']))
        logger.debug('getInfo:\n{}'.format(l))
        return l

    def attack(self):
        """
        Check if vHack server botnet is attackable,
        then attack if can.
        :return: none
        """
        self._initbot()
        logger.info("Trying Bot Net")
        cinfo = self.getInfo()
        
        for i in range(1, self.botNetServers + 1):
            if cinfo[i-1] == '1':
                logger.debug('attacking #{}'.format(i))
                if i == 1:
                    response = self.ut.requestString(self.username, self.password, self.uhash, "vh_attackCompany.php", company=str(i))
                else:
                    response = self.ut.requestString(self.username, self.password, self.uhash, "vh_attackCompany" + str(i) + ".php", company=str(i))
                logger.debug('attack #{} response {}'.format(i, response))
                if response == '0':
                    logger.info('#{} Netcoins gained'.format(i))
                else:
                    logger.info('#{} Failed! No netcoins...'.format(i))
            else:
                logger.info("Botnet #{} not hackable as yet".format(i))

    def upgradebotnet(self):
        """
        Check if there is enough money to upgrade a botnet PC.
        Cycle through and upgrade until no money.
        :return: None
        """
        logger.info("Attempting to upgrade bot net PC's")
        for i in self.botnet:
            if i.botupgradable():
                while int(self.p.getmoney()) > int(i.nextlevelcost()):
                    new_bal = i.upgradesinglebot()
                    if new_bal is not None:
                        self.p.setmoney(new_bal)
                logger.debug("#{}({}) not enough money".format(i.id, i.lvl))
            logger.debug("#{}({}) not upgradeable".format(i.id, i.lvl))

    def _botnetInfo(self):
        """
        Get the botnet information including vHack servers and PC data.
        :return: string
        '{"count":"14",
        "data":[{"bID":"1","bLVL":"100","bSTR":"100","bPRICE":"10000000"},
        {"bID":"2","bLVL":"100","bSTR":"100","bPRICE":"10000000"}],
        "strength":23,"resethours1":"","resetminutes1":"14","resethours2":"4","resetminutes2":"15",
        "resethours3":"3","resetminutes3":"15",
        "canAtt1":"2","canAtt2":"2","canAtt3":"2"}'
        """
        temp = self.ut.requestString(self.username, self.password, self.uhash, "vh_botnetInfo.php")
        return temp

    def __repr__(self):
        return "Botnet details: vHackServers: {0}, Bot Net PC's: {1}".format(self.botNetServers, self.botnet)


class Bot:
    ut = Utils()

    def __init__(self, botid, botlvl, price, username, password, uhash):
        self.id = int(botid)
        self.lvl = int(botlvl)
        self.username = username
        self.uhash = uhash
        self.password = password
        self.upgradecost = int(price)

    def botupgradable(self):
        """
        Determine if botnet PC is at max level or not.
        :return: Bool
        """
        if self.lvl < 100:
            return True
        else:
            return False

    def nextlevelcost(self):
        """
        Return the cost of upgrading bot to the next level
        :return:int
        """
        return self.upgradecost

    def upgradesinglebot(self):
        """
        Pass in bot class object and call upgrade function based on bot ID.
        details :
        {u'strength': u'22', u'old': u'30', u'mm': u'68359859',
        u'money': u'66259859', u'costs': u'2100000',
        u'lvl': u'21', u'new': u'22'}
        current lvl, bot number, x, x, upgrade cost, lvl, next lvl
        :return: None
        """
        response = self.ut.requestString(self.username, self.password, self.uhash, "vh_upgradeBotnet.php", bID=str(self.id))
        details = json.loads(response)
        try:
            self.upgradecost = details['costs']
            self.lvl = details['new']
            logger.info("Bot # {0} upgraded to level {1} at a cost of {2} $".format(details['old'], details['lvl'], details['costs']))
        except TypeError as e:
            logger.info("Bot fully upgraded, should not get this error. Fix me! {0}".format(e))
            return None
        try:
            return details['money']
        except TypeError as e:
            logger.info("Error in upgradesinglebot: {0}".format(e))
            return None

    def __repr__(self):
        return "Bot details: id: {0}, Level: {1}, Next Cost: {2}".format(self.id, self.lvl, self.upgradecost)
