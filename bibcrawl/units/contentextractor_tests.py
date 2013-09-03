import unittest
from bibcrawl.units.mockserver import MockServer, dl
from bibcrawl.spiders.contentextractor import ContentExtractor

class SpidersUnitTests(unittest.TestCase):

  def _checkContentXPath(self, rss, page, xpath):
    with MockServer():
      extractor = ContentExtractor(dl(rss))
      extractor.feed(dl(page), "http://" + page)
    extractor._refresh()
    self.assertEqual(extractor.xPaths[0], xpath)

  def testMnmlist(self):
    self._checkContentXPath(
        "mnmlist.com/feed",
        "mnmlist.com/suitcase/",
        "//*[@class='entry']")

  def _mh(self, post):
    self._checkContentXPath(
        "meinrhyme.wordpress.com/feed",
        "meinrhyme.wordpress.com/2013/09/03/{}/".format(post),
        "//*[@class='entry-content']")

  def testMeinrhymePost1th(self):
    self._mh("modern-mother-goose-on-the-loose-366-a-day-at-the-zoo")
  def testMeinrhymePostAd1(self):
    self._mh("the-need-to-read-264-2")
  def testMeinrhymePostAin(self):
    self._mh("three-reasons-to-wait-on-a-train-2005")
  def testMeinrhymePostAit(self):
    self._mh("three-places-to-wait-2009")
  def testMeinrhymePostAme(self):
    self._mh("three-to-fight-at-the-game-2013")
  def testMeinrhymePostAns(self):
    self._mh("three-known-facts-about-politicians-2004")
  def testMeinrhymePostArd(self):
    self._mh("three-ways-to-know-that-picking-beans-is-really-hard-2010")
  def testMeinrhymePostAy1(self):
    self._mh("the-highlight-of-the-day-in-my-own-way-521-3")
  def testMeinrhymePostBle(self):
    self._mh("three-types-of-cable-2010")
  def testMeinrhymePostDay(self):
    self._mh("three-possible-noises-to-hear-today-2013")
  def testMeinrhymePostDay(self):
    self._mh("three-that-were-baked-yesterday-2010")
  def testMeinrhymePostEar(self):
    self._mh("three-things-that-men-do-not-fear-2010")
  def testMeinrhymePostHym(self):
    self._mh("a-childs-time-in-simple-rhyme-531")
  def testMeinrhymePostIse(self):
    self._mh("three-things-that-politicians-raise-2006")
  def testMeinrhymePostLls(self):
    self._mh("three-places-to-find-other-oil-spills-2010")
  def testMeinrhymePostN1w(self):
    self._mh("the-highlight-of-the-day-in-my-own-way-25")
  def testMeinrhymePostNer(self):
    self._mh("three-places-you-might-suspect-to-see-a-body-scanner-2013")
  def testMeinrhymePostNts(self):
    self._mh("three-movements-2013")
  def testMeinrhymePostOrk(self):
    self._mh("three-important-benefits-at-work-2007")
  def testMeinrhymePostWay(self):
    self._mh("three-reasons-you-should-not-speed-on-the-freeway-2003")
  def testMeinrhymePostY12(self):
    self._mh("three-for-today-2013-2")

  # def _qd(self, post):
  #   self._checkContentXPath(
  #     "www.quantumdiaries.org/feed",
  #       "www.quantumdiaries.org/2013/08/{}/".format(post),
  #       "//*[@class='entry']")

  # def testQuantumPost28h(self):
  #   self._qd("28/higgs-hunting-in-progress")
  # def testQuantumPost25g(self):
  #   self._qd("25/girls-at-cern-loads-of-em")
  # def testQuantumPost23i(self):
  #   self._qd("23/ilc-more-than-just-a-higgs-factory")
  # def testQuantumPost21v(self):
  #   self._qd("21/visiting-my-high-school-in-arkansas")
  # def testQuantumPost21a(self):
  #   self._qd("21/at-fermilab-national-accelerator-is-our-middle-name")
  # def testQuantumPost20c(self):
  #   self._qd("20/can-string-theory-predict-stuff")
  # def testQuantumPost19a(self):
  #   self._qd("19/a-fresh-look-for-the-standard-model")
  # def testQuantumPost18m(self):
  #   self._qd("18/mother-hunting-at-cern")
  # def testQuantumPost11c(self):
  #   self._qd("11/confessions-of-a-cern-summer-student")
  # def testQuantumPost09s(self):
  #   self._qd("09/snowmass-take-away")
  # def testQuantumPost09n(self):
  #   self._qd("09/notre-univers-est-le-votre")
  # def testQuantumPost09o(self):
  #   self._qd("09/our-universe-is-yours")
  # def testQuantumPost08j(self):
  #   self._qd("08/join-the-dots-to-measure-antimatter")
  # def testQuantumPost08f(self):
  #   self._qd("08/fermilab-accelerator-complex-starts-up-after-long-shutdown")
  # def testQuantumPost07w(self):
  #   self._qd("07/wedding-cake")

  # def _kb(self, post):
  #   self._checkContentXPath(
  #       "korben.info/feed",
  #       "korben.info/{}.html".format(post),
  #       "//*[@class='post-content']")

  # def testKorbenPost100(self):
  #   self._kb("10-places-de-cine-a-gagner")
  # def testKorbenPost800(self):
  #   self._kb("80-bonnes-pratiques-seo")
  # def testKorbenPostApp(self):
  #   self._kb("app-gratuite-amazon")
  # def testKorbenPostArn(self):
  #   self._kb("arnaque-au-blogueur")
  # def testKorbenPostBey(self):
  #   self._kb("beyond")
  # def testKorbenPostCes(self):
  #   self._kb("cest-la-rentree-2")
  # def testKorbenPostChe(self):
  #   self._kb("cheat-pour-vous-souvenir-de-la-bonne-syntaxe")
  # def testKorbenPostCon(self):
  #   self._kb("convertir-une-photo-en-fichier-excel")
  # def testKorbenPostCre(self):
  #   self._kb("creer-police-de-caractere-birdfont")
  # def testKorbenPostDef(self):
  #   self._kb("defcon-le-documentaire")
  # def testKorbenPostDes(self):
  #   self._kb("des-etoiles-lors-de-la-saisie-dun-mot-de-passe-dans-le-terminal")
  # def testKorbenPostDro(self):
  #   self._kb("dronestagram")
  # def testKorbenPostEmb(self):
  #   self._kb("embrouillez-ceux-qui-surveillent-vos-habitudes-de-surf")
  # def testKorbenPostEta(self):
  #   self._kb("etag-tracking")
  # def testKorbenPostFor(self):
  #   self._kb("forever-and-ever")
  # def testKorbenPostGam(self):
  #   self._kb("game-of-thrones-saison-3-les-effets-speciaux")
  # def testKorbenPostIns(self):
  #   self._kb("installer-silverlight-sous-linux")
  # def testKorbenPostNgr(self):
  #   self._kb("ngrok-creer-un-tunnel-pour-vos-applications-locale")
  # def testKorbenPostOrb(self):
  #   self._kb("orbit-downloader")
  # def testKorbenPostRep(self):
  #   self._kb("reparez-votre-office-365-avec-offcat")
  # def testKorbenPostRoo(self):
  #   self._kb("rooter-windows-rt")
  # def testKorbenPostSau(self):
  #   self._kb("sauvegarder-photos-telephone-sur-ordinateur")
  # def testKorbenPostSup(self):
  #   self._kb("super-parkour-bros")
  # def testKorbenPostThu(self):
  #   self._kb("thunderbird-recherche-globale-ne-fonctionne-plus")
  # def testKorbenPostTro(self):
  #   self._kb("trouver-gif-anime")
  # def testKorbenPostTro(self):
  #   self._kb("trouver-partition-chiffree")
  # def testKorbenPostUnn(self):
  #   self._kb("un-documentaire-a-ne-pas-manquer-sur-les-bio-hackers")
  # def testKorbenPostVib(self):
  #   self._kb("viber-linux")
  # def testKorbenPostWin(self):
  #   self._kb("windroy-android-sur-votre-pc-windows")
  # def testKorbenPostWor(self):
  #   self._kb("word-ouvrir-automatiquement-le-dernier-document-au-lancement")

  # def _hp(self, post):
  #   self._checkContentXPath(
  #       "www.huffingtonpost.com/feed",
  #       "www.huffingtonpost.com/{}.html".format(post),
  #       "//*[@class='entry_body_text']")

  # def testHuffingtonPost01(self):
  #   self._hp("michael-roth/review-of-derek-boks-high_b_3855201")
  # def testHuffingtonPost22(self):
  #   self._hp("leo-w-gerard/we-shall-overcome_b_3844622")
  # def testHuffingtonPost32(self):
  #   self._hp("jan-schakowsky/to-celebrate-labor-day-gi_b_3855532")
  # def testHuffingtonPost36(self):
  #   self._hp("michael-brune/working-on-a-dream_b_3857236")
  # def testHuffingtonPost48(self):
  #   self._hp("raymond-j-learsy/frances-cri-de-guerre_b_3854648")
  # def testHuffingtonPost65(self):
  #   self._hp("chris-weigant/congress-labor-daze_b_3857465")
  # def testHuffingtonPost72(self):
  #   self._hp("jim-sleeper/hidden-truths-about-ameri_b_3853172")
