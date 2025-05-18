import re
from typing import Dict, Tuple, List, Any
from symspellpy.symspellpy import SymSpell
import ftfy
import string
import pkg_resources
import geopandas as gpd

# sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
# dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
# sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)


def join_hyphenated_words(text: str) -> str:
    return re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

def normalize_newlines(text: str) -> str:
    return re.sub(r'\n+', ' ', text)

def remove_standalone_hyphens(text: str) -> str:
    return re.sub(r'\s+-\s+', ' ', text)

def remove_hyphen_start_line(text: str) -> str:
    return re.sub(r'^\s*-\s*', '', text, flags=re.MULTILINE)

# def clean_text(text):
#     text = ftfy.fix_text(text)
#     text = remove_punctuation(text)
#     text = join_hyphenated_words(text)
#     text = normalize_newlines(text)
#     text = remove_standalone_hyphens(text)
#     text = remove_hyphen_start_line(text)
    
#     sentences = re.split(r'(?<=[.!?])\s+', text)
#     corrected = ""
#     for sentence in sentences:
#         suggestion = sym_spell.lookup_compound(sentence, max_edit_distance=1)
#         if suggestion:
#             corrected += suggestion[0].term + " "
#         else:
#             corrected += sentence + " "
#     corrected = corrected.lower()
#     return corrected.strip()

def clean_text(text: str) -> str:
    # Use cached version for repeated patterns
    text = ftfy.fix_text(text)
    text = remove_punctuation(text)
    text = join_hyphenated_words(text)
    text = normalize_newlines(text)
    text = remove_standalone_hyphens(text)
    text = remove_hyphen_start_line(text)
    
    # No need to split and join sentences anymore
    return text.lower().strip()


def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans('', '', string.punctuation))

def read_gpkg_to_dict(gpkg_path: str) -> Dict[str, Tuple[float, float]]:
    """
    Read GPKG file and convert to dictionary with names as keys and coordinates as values.
    
    Args:
        gpkg_path: Path to the GPKG file
        
    Returns:
        Dictionary with names as keys and (x, y) coordinates as values
    """
    # Read the GPKG file
    gdf = gpd.read_file(gpkg_path)
    
    # Create dictionary with names as keys
    coord_dict: Dict[str, Tuple[float, float]] = {}
    
    for _, row in gdf.iterrows():
        # Extract coordinates from Point geometry
        coords = (row.geometry.x, row.geometry.y)
        name = row['name']

        

        coord_dict[name] = coords
    
    return coord_dict


if __name__ == "__main__":

    bad_ocr: str = "Edinburgh, jamshedpur, March zi. i68j.\n\nH E Convention is stiM busy\nin feeling the Militia; and\n\nff prosecuting the other Me-\n\nthods laid down for the se-\n\nt curing the Peace of the\nCountry, and putting the seme in a Po-\nsture of Defence, in cafe of Insurrection\n.or Invasion., In particular, great carp is\ntaken, that the Western Counties , which\nlye next to Ireland, be in readiness; and\nOrders are given for Disarming the Pa-\npists, and Mustering the Militia. The\nEarl of Marry the Governor of Stirling-\nCastle, being Sick, the Convention sent\nSir Charles A skin to Stirling , to see to\nthe Security of that Town and Castle,\nwhich he hath done 5 and bath writ to\nthe Convention, that he is in Possession of\nthe Castle, and will maintain it for their\nService.\n\nThe Treaty betwixt the Duke of\n\nGourdon and the Convention,for the Sur-\nrendring the Castle of Edinburgh, was al-\niDoltconcluded, so that it was believed\nthat he would leave it the next day How-\never he had sent a Lester co the House,\nin which be insinuated to them, the e-\nspousing of K. James's Interest, who he\nsaid,was in foW.and offers to go wait\nupon him, in order to obtain assurance\nof feeling Religion and Laws, to their\nContentment,and upon lasting and fare\nfoundations; but the House did not at\n§U> take notice of this part of the Letter.\n\nThe Town of Surhng being inform-\n\ned/that the Earl ofDundee was coming\nthat way with zoo Hor fe?they put' them-\nselves in a Posture of keeping him from\nentring the Town. It's-said, he is gone\nWeft* it's thought with a design to go\nover .to Ireland* ..5*1\n\nf\n\n.....PHHRH l0\n\nadvance It immediately uponthe Seen-\nrity of the Conventions -\n; Many of the best Men Which were\nwith the Earl of Qundee> have left him\n\nThe Messenger King James sent with\n\nhis Letter tbrthe Convention being\nkept in Custody, or Under Bail, wa*\nthis Day released, and dismissed' with\na Pass, instead of an Answer.\n\nOn Monty fast, The Convention\n\npassed art ^ct s' appqintftig she Seft\nSupply, Custom and Ekctse y and all\nthe Crown-Rerits apd Reverts, to be\napplied tqwanfr'payingtheFdfcesKing\nWilliam of England should send , and\nthose to be raised here, for defending\n\nF , this\n\nSome Ships do appear in the Frith >in\n\nwhich it's hoped Major General Mackay\nmay be with the three Regiments.\n\nTheDuke of Qjisensberryfirid the Earl\n\nof Cafe Us, and some others, arrived\nyesternight, but have not yet been in\nthe Convention, of which several of the\nMembers were sick, and1 several absenr.\n\nThe Convention hath sent an Express\n\nto Ireland, to know the Truth of the\nNews, that they hear from that King-\ndom , and hath appointed two (mall\nx Frigats to Cruise betwixt'Scotland and\nIreland, to bring them Intelligence j and\nall Protestants are allowed to import\ninto that Kingdom Arms aud Ammuni-.\ntion,sor which the Estates wist pay them.\n\nThe Forces that came from she Weft*\n\nbeing above 6006 Men, are ordered\none Week's pay', and the publick Thanks\nof rhe House for their good Service, in\nblocking up the Castle.\n\nIn regard the Publick Revenues can-\n\nnot be got in so foon as is necessary,\nfor paying off the Soldiery; The Mer-\n\nthisKingdom,and tbeProtestantReligion\n\nEdinburgh the i$d Instant. D. Gattr-.'\n\nde tent bis l^strPrpppfals ycith'a Moni-\ntor js Letter td the'Cofi veh ti6n, .mi ndi ng\nthem of what Honours and Dignities\nKing James's Predecessors had raised\nmost, or m&ny|£f them ed , and what\nMarks of RdyalFavour arid Bounty he\nhadconfefrr'don them; and which ought\nnot to be forgot for the Errors and Mis-\ncarriages of jpodjr Four Years Reign |\nand if they tfould a$ow hirnLiberty to\ngo over tolriland, Where he is informed\nKing jfemes now is, he would endea-\nvour an Accommodation between Him\nand the Estates of the Kingdom, to\nhave Religion , Laws, Liberty, and\nProperty restored and established. ~JBut\nthis Motion of the Duke, and his Under-\ntaking, was altogether rejected, without\nsuffering the said Monitory to be entred\nin their Journals, that they bad recei-\nved or read it. His^Demands were',\ni. An A^.of Indemnity for himself, and\nall Papists and protestants that serve un-\nder him in the, Castle,, and for Four or\nFive Priests. might be secu-\nred against the Strangers or Cameronidni,\nwhom he calls the Rabble,, in and about\nthe JTowsst, his epipiog put/ 3. That\nfie might have a.Guard of 40 Horse to\nConduct hiny.\nw To the > ijl, {the Convention anfwer-\ned, That they would give Security to\n-him and others, in their Lives and For-\ntune^,-so far as they had Acted as Pa-\npists j and that the Priests should have\nPasses to^depart the Kingdom, on con-\nditionnever tpreturn agaip-m .\n\nTo the zd, That he should have the\n\nGuard he demanded,, till tie were over\n.the Water tp.Brunteland.\n\n• To the ,3 dt That a like number of\nGuards stiould Convey him from thenCe\njiomeward , v which should be disbanded\nwithin 24-feJours after his Arrival, he gi-\nving security to stye peaceably,and,qot\ndisturb tbe^Peace of the ICmgdom\n\n^Tbjsdaya Proclam^tson was issued\nfprth,cqmm^nding all the Papists, who\nare-got $ouse-keepeVs,j to„ eseparcTen\nmiles put pfTown* in few days, and\nfor biddigg.them. tc?.car/y^ any. Asms, ex-\ncept a Swo^d pnly.\nn Lor4rPand& beforeJae left the Town,\ndesired jheu^nyehtioh to seqd.an An- .\nswe^so;K.^^j's;Left^r^ but they told\nhim by aJM:aper\\ that he need not stay .\nfor that, fogihyy had hdjrie.co fendi Tlsen\nhe urged for a Pafs to go.Tor Ireland,\n\nm I\n\nwhich was likewise refused hill).\n\nMost part of the controverted Electi-\n\nons being determin'd, Vulw.art, and Sir\nDuncan Cambel of AUch'inbreck, and\"o-\nther forfeited Barons, were allowed to\nSit in the^Conyention.\nNotwithstanding the Articles agreed on\nbetwixt the Convention, and DJGcurdon,\nabout surrender of the Gaftle.it is not yet\nsurrendred; he pretending now to have\na Letter from K. James out of Ireland,\nof which,.desirous to express bis Joy, by\nFiring the Guns, he gave notice to the\nCity, that they might not be alarmed\nat it, since he designed them no harm\nall which is believed ro be a (ham.\n\nD. Hamilton manages King William's\n\nInterest here,with much Zeal) Prudence,\narid Diligence. Efy Letters from Ireland\n'sis reported there, That King James is\nhere in Scotland, raising men to go over\nfor England,:, and here 'cis reported\nby those of his Party „ That he is\njp 'Ireland, » .raising an Army for\nto bring over hither ; but it's believed\nby ail here, except Papists and Malig-\njiants, that he is no more in Ireland than\nhere, and Praised be God, he is no more\nhere than in England.\n\nThe Castle is blockt up, and none\n\nsuffered to go in, or come out, and\nsome small Picqueering happens betwixt\nthe Garifon arid Guard.\n\nThe Duke' if SHueensbefry, and Earl\n\nof Kintore, are lately Arnved, and are\nvery well inclined to Advance King Wil-\nliams Interest, and the Weal and Quiet\n,pf the KingdpmiandProtestant Religion,\n1 This day tbu Letter to His Majesty\nof England, was Signed in a Meeting\nof the whole House, except some few\ndisaffected.Persops, and Ordered to be\n.immediately sent away by the Lord\nRosy j who has taken Post this Afternoon\nfor London..\ns.. This day an Act passed, recommend-\ning to,all Sheriffs of Counties, Magi-\nstrates of Boroughs, Collonels and\nCommanders of the Militia, and Forces,\nthat care be taken upPn all the High-\nways, Passages, Posts, and Ferries, that\nnone (Trayel with Horses and Arms,\nwithout Passes j unless' they be able to\ngive a good Account of themselves, and\nto fecure all such Persons as Travel o-\ntherwl.fe, Which Was Published and\nProclaimed al the Market-Cross.\n\n"
    print(clean_text(bad_ocr))