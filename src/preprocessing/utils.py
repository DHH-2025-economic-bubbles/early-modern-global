from pathlib import Path
import re
from typing import Dict, Tuple, List, Any
from symspellpy.symspellpy import SymSpell
import ftfy
import string
import pkg_resources
import geopandas as gpd





sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)


# Precompile patterns for better performance
HYPHENATED_WORDS_PATTERN = re.compile(r'(\w)-\s*\n\s*(\w)')
NEWLINES_PATTERN = re.compile(r'\n+')
HYPHENS_PATTERN = re.compile(r'(?:\s+-\s+|^\s*-\s*)', re.MULTILINE)

def clean_text(text: str) -> str:
    text = ftfy.fix_text(text)
    text = remove_punctuation(text)
    
    # Use precompiled patterns
    text = HYPHENATED_WORDS_PATTERN.sub(r'\1\2', text)
    text = NEWLINES_PATTERN.sub(' ', text)
    text = HYPHENS_PATTERN.sub(' ', text)

    suggestion = sym_spell.lookup_compound(text, max_edit_distance=2)
    if suggestion:
        corrected = suggestion[0].term
    else:
        corrected = text

    
    return corrected.lower().strip()


def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans('', '', string.punctuation))

def read_gpkg_to_dict(gpkg_path: str) -> Dict[str, Tuple[float, float]]:

    gdf = gpd.read_file(gpkg_path)
    
    coord_dict: Dict[str, Tuple[float, float]] = {}
    
    for _, row in gdf.iterrows():
        coords = (row.geometry.x, row.geometry.y)
        name = row['name']
        coord_dict[name] = coords
    
    return coord_dict

def regroup_texts(text_to_explode) -> List[str]:
    """
    Regroups paragraphs in the text according to the following rules:
    1. All single-line paragraphs (separated by "\n\n" and not containing "\n") 
       should be grouped with the closest next paragraph that has at least one "\n" in it.
    2. Multiple consecutive single-line paragraphs will be grouped together until a multi-line
       paragraph is found.
    3. Paragraphs that have only 1 or 2 newline characters ("\n") are removed from the result.
    4. Paragraphs that have 15 or fewer actual characters (excluding newlines) are removed from the result.
    5. Paragraphs that have an average of fewer than 10 actual characters per line are removed.
    
    Args:
        text_to_explode (str): The input text to be regrouped
        
    Returns:
        List[str]: A list of regrouped paragraphs with filtered content
    """
    # Split the text by double newlines
    paragraphs = text_to_explode.split("\n\n")
    result = []
    
    # Keep track of accumulated single-line paragraphs
    buffer = []
    
    for i, para in enumerate(paragraphs):
        current_para = para.strip()
        is_single_line = "\n" not in current_para
        
        if is_single_line:
            # Add to buffer
            buffer.append(current_para)
        else:
            # Found a multi-line paragraph
            if buffer:
                # Combine all buffered single-line paragraphs with this multi-line paragraph
                combined = " ".join(buffer) + " " + current_para
                result.append(combined)
                buffer = []  # Clear the buffer
            else:
                # No buffered single-line paragraphs, just add the multi-line paragraph
                result.append(current_para)
    
    # If there are any remaining single-line paragraphs in the buffer
    if buffer:
        result.append(" ".join(buffer))
    
    # Filter out paragraphs based on criteria
    filtered_result = []
    for para in result:
        # Count the number of newlines in the paragraph
        newline_count = para.count('\n')
        
        # Count actual characters (excluding newlines)
        actual_char_count = len(para.replace('\n', ''))
        
        # Calculate average actual characters per line
        lines = para.split('\n')
        num_lines = len(lines)
        avg_chars_per_line = sum(len(line) for line in lines) / num_lines if num_lines > 0 else 0
        
        # Conditions to keep a paragraph:
        # 1. Either has 0 newlines (single line) OR more than 2 newlines
        # 2. Has more than 15 actual characters total (excluding newlines)
        keep_paragraph = (
            (newline_count > 2) and 
            actual_char_count > 15
        )

        if keep_paragraph:
            filtered_result.append(para)
    
    return filtered_result


if __name__ == "__main__":
    bad_ocr: str = "Edinburgh, jamshedpur, March zi. i68j.\n\nH E Convention is stiM busy\nin feeling the Militia; and\n\nff prosecuting the other Me-\n\nthods laid down for the se-\n\nt curing the Peace of the\nCountry, and putting the seme in a Po-\nsture of Defence, in cafe of Insurrection\n.or Invasion., In particular, great carp is\ntaken, that the Western Counties , which\nlye next to Ireland, be in readiness; and\nOrders are given for Disarming the Pa-\npists, and Mustering the Militia. The\nEarl of Marry the Governor of Stirling-\nCastle, being Sick, the Convention sent\nSir Charles A skin to Stirling , to see to\nthe Security of that Town and Castle,\nwhich he hath done 5 and bath writ to\nthe Convention, that he is in Possession of\nthe Castle, and will maintain it for their\nService.\n\nThe Treaty betwixt the Duke of\n\nGourdon and the Convention,for the Sur-\nrendring the Castle of Edinburgh, was al-\niDoltconcluded, so that it was believed\nthat he would leave it the next day How-\never he had sent a Lester co the House,\nin which be insinuated to them, the e-\nspousing of K. James's Interest, who he\nsaid,was in foW.and offers to go wait\nupon him, in order to obtain assurance\nof feeling Religion and Laws, to their\nContentment,and upon lasting and fare\nfoundations; but the House did not at\n§U> take notice of this part of the Letter.\n\nThe Town of Surhng being inform-\n\ned/that the Earl ofDundee was coming\nthat way with zoo Hor fe?they put' them-\nselves in a Posture of keeping him from\nentring the Town. It's-said, he is gone\nWeft* it's thought with a design to go\nover .to Ireland* ..5*1\n\nf\n\n.....PHHRH l0\n\nadvance It immediately uponthe Seen-\nrity of the Conventions -\n; Many of the best Men Which were\nwith the Earl of Qundee> have left him\n\nThe Messenger King James sent with\n\nhis Letter tbrthe Convention being\nkept in Custody, or Under Bail, wa*\nthis Day released, and dismissed' with\na Pass, instead of an Answer.\n\nOn Monty fast, The Convention\n\npassed art ^ct s' appqintftig she Seft\nSupply, Custom and Ekctse y and all\nthe Crown-Rerits apd Reverts, to be\napplied tqwanfr'payingtheFdfcesKing\nWilliam of England should send , and\nthose to be raised here, for defending\n\nF , this\n\nSome Ships do appear in the Frith >in\n\nwhich it's hoped Major General Mackay\nmay be with the three Regiments.\n\nTheDuke of Qjisensberryfirid the Earl\n\nof Cafe Us, and some others, arrived\nyesternight, but have not yet been in\nthe Convention, of which several of the\nMembers were sick, and1 several absenr.\n\nThe Convention hath sent an Express\n\nto Ireland, to know the Truth of the\nNews, that they hear from that King-\ndom , and hath appointed two (mall\nx Frigats to Cruise betwixt'Scotland and\nIreland, to bring them Intelligence j and\nall Protestants are allowed to import\ninto that Kingdom Arms aud Ammuni-.\ntion,sor which the Estates wist pay them.\n\nThe Forces that came from she Weft*\n\nbeing above 6006 Men, are ordered\none Week's pay', and the publick Thanks\nof rhe House for their good Service, in\nblocking up the Castle.\n\nIn regard the Publick Revenues can-\n\nnot be got in so foon as is necessary,\nfor paying off the Soldiery; The Mer-\n\nthisKingdom,and tbeProtestantReligion\n\nEdinburgh the i$d Instant. D. Gattr-.'\n\nde tent bis l^strPrpppfals ycith'a Moni-\ntor js Letter td the'Cofi veh ti6n, .mi ndi ng\nthem of what Honours and Dignities\nKing James's Predecessors had raised\nmost, or m&ny|£f them ed , and what\nMarks of RdyalFavour arid Bounty he\nhadconfefrr'don them; and which ought\nnot to be forgot for the Errors and Mis-\ncarriages of jpodjr Four Years Reign |\nand if they tfould a$ow hirnLiberty to\ngo over tolriland, Where he is informed\nKing jfemes now is, he would endea-\nvour an Accommodation between Him\nand the Estates of the Kingdom, to\nhave Religion , Laws, Liberty, and\nProperty restored and established. ~JBut\nthis Motion of the Duke, and his Under-\ntaking, was altogether rejected, without\nsuffering the said Monitory to be entred\nin their Journals, that they bad recei-\nved or read it. His^Demands were',\ni. An A^.of Indemnity for himself, and\nall Papists and protestants that serve un-\nder him in the, Castle,, and for Four or\nFive Priests. might be secu-\nred against the Strangers or Cameronidni,\nwhom he calls the Rabble,, in and about\nthe JTowsst, his epipiog put/ 3. That\nfie might have a.Guard of 40 Horse to\nConduct hiny.\nw To the > ijl, {the Convention anfwer-\ned, That they would give Security to\n-him and others, in their Lives and For-\ntune^,-so far as they had Acted as Pa-\npists j and that the Priests should have\nPasses to^depart the Kingdom, on con-\nditionnever tpreturn agaip-m .\n\nTo the zd, That he should have the\n\nGuard he demanded,, till tie were over\n.the Water tp.Brunteland.\n\n• To the ,3 dt That a like number of\nGuards stiould Convey him from thenCe\njiomeward , v which should be disbanded\nwithin 24-feJours after his Arrival, he gi-\nving security to stye peaceably,and,qot\ndisturb tbe^Peace of the ICmgdom\n\n^Tbjsdaya Proclam^tson was issued\nfprth,cqmm^nding all the Papists, who\nare-got $ouse-keepeVs,j to„ eseparcTen\nmiles put pfTown* in few days, and\nfor biddigg.them. tc?.car/y^ any. Asms, ex-\ncept a Swo^d pnly.\nn Lor4rPand& beforeJae left the Town,\ndesired jheu^nyehtioh to seqd.an An- .\nswe^so;K.^^j's;Left^r^ but they told\nhim by aJM:aper\\ that he need not stay .\nfor that, fogihyy had hdjrie.co fendi Tlsen\nhe urged for a Pafs to go.Tor Ireland,\n\nm I\n\nwhich was likewise refused hill).\n\nMost part of the controverted Electi-\n\nons being determin'd, Vulw.art, and Sir\nDuncan Cambel of AUch'inbreck, and\"o-\nther forfeited Barons, were allowed to\nSit in the^Conyention.\nNotwithstanding the Articles agreed on\nbetwixt the Convention, and DJGcurdon,\nabout surrender of the Gaftle.it is not yet\nsurrendred; he pretending now to have\na Letter from K. James out of Ireland,\nof which,.desirous to express bis Joy, by\nFiring the Guns, he gave notice to the\nCity, that they might not be alarmed\nat it, since he designed them no harm\nall which is believed ro be a (ham.\n\nD. Hamilton manages King William's\n\nInterest here,with much Zeal) Prudence,\narid Diligence. Efy Letters from Ireland\n'sis reported there, That King James is\nhere in Scotland, raising men to go over\nfor England,:, and here 'cis reported\nby those of his Party „ That he is\njp 'Ireland, » .raising an Army for\nto bring over hither ; but it's believed\nby ail here, except Papists and Malig-\njiants, that he is no more in Ireland than\nhere, and Praised be God, he is no more\nhere than in England.\n\nThe Castle is blockt up, and none\n\nsuffered to go in, or come out, and\nsome small Picqueering happens betwixt\nthe Garifon arid Guard.\n\nThe Duke' if SHueensbefry, and Earl\n\nof Kintore, are lately Arnved, and are\nvery well inclined to Advance King Wil-\nliams Interest, and the Weal and Quiet\n,pf the KingdpmiandProtestant Religion,\n1 This day tbu Letter to His Majesty\nof England, was Signed in a Meeting\nof the whole House, except some few\ndisaffected.Persops, and Ordered to be\n.immediately sent away by the Lord\nRosy j who has taken Post this Afternoon\nfor London..\ns.. This day an Act passed, recommend-\ning to,all Sheriffs of Counties, Magi-\nstrates of Boroughs, Collonels and\nCommanders of the Militia, and Forces,\nthat care be taken upPn all the High-\nways, Passages, Posts, and Ferries, that\nnone (Trayel with Horses and Arms,\nwithout Passes j unless' they be able to\ngive a good Account of themselves, and\nto fecure all such Persons as Travel o-\ntherwl.fe, Which Was Published and\nProclaimed al the Market-Cross.\n\n"
    
    text_to_explode = "iT;e have taken tiro or three Opportunities, in the\n\nIntervals of Foreign Mails, to make Extracts\nout of a Book which we think truly valuable,\nnot only for the General Notions of Trade\nit contains, but also for the excellent Charts, and\nDirections for Sailing, thereto annex'd; which\nrender it the most Useful Work of the kind ex-\ntaut. And having now an Opportunity to re-\nfume that Subject, we shall {as we have Room)\ninsert that Author's Thoughts of the English\nColonies in America, which may perhaps give\nsome necessary Hints to some of our Readers\nthat trade to those Parts. The Book we extract\nfrom is entitled, the Atlas Maritimus &\nCommercialis ; or a General View of the\nWorld, so far as relates to Trade and Na-\nvigation ; a SubjeCt upon which too much can-\nnot be said.\n\nH E Ergiish Colonies in Ame-\nrica are divided into two Parts.\n(1.) Their Island Colonies.\n( 2 ) Their Colonies on the\nContinent. The Island Co-\nlonies are,\n\nBarbadoes, I S. Christophers,\nJamaica, I Tobago, not planted.\nAntigua, ! Bermuda,\nNevis, Newfoundland,\nMomserat, [ New Providence, not planted.\n\nThe Settlements of these are not Factories,\n\nForts and Castles, as in the last Indies, or\non the Coast of Africa, for the Protection of\nour Merchants and of their Trade, against the\nNatives ; but these are the British Pa-\ntrimony, and may be called their own in So-\nvereignty ; they are Part of the King of Great\nBritain's Dominions ; all the Inhabitants are\nhis Subjects, or -the Slaves of his Subjects,\nnone excepted : Nor has any Prince in the\nW'rid any Claim to them, or any Part of\nthem, but the King of Great Britain.\n\nThis is necessary to be premised, because\n\nhaving in our Discourse of the British Irade\naccounted for the Produce of these Colonies\nas the Produce of the British Kingdom, and\nthe Consumption of European Goods, as the\nBritish Home Consumption, it ought not to\nappear wrong that those things are not re-\npeated again here.\n\nThe Produce of the first six of these Islands\n\nis (a few Articles only excepted) much the\nfame one with another as to Trade ; that is\nto fay,\n\nC Sugar,\n\nTho I Ginger,\n\nPimento, 7 These three\nIndigo, > chiefly at\n\nOO .\n\nOriginal^\nGrowth 1\n\nL Cotton, Jamaica.\n\n(2.) The\\\nSecondary^\nProduct,\nsuch as, Molasses,\n\nSuccades,\nRum,\nCitron Water,\nLime Juice.\n\nDrtigs^ fContrayerva,\n\nj Cypeias,\n’ Adjunctum Nigrura,\nCucumis Agreslis,\nAccacia,\nSassafras,\nYellow Saiinders,\nMauchivel,\nSea Feather,\nRock Salt,\n( Lignum Vitas,\nLMaftick, Locust Tree,’\n\nAchiotte,\nGuajacum,\nChifia Root,\nSarsaparilla,\nCasiia,\nBenjamin,\nTamarinds,\nVanilloes,\nMifletoe,\nAloes Epatica,\nSperma Cœti. S\n\nW\n\nc\n\na\n\nt\n\nt\nS\ni\n\nt\nT\ns\nP\n\nt\n\ns\n\na\nf\nfi\ng\nw\nF\n\nThe Bermudas produce\n\nWood, and\n\nr , C Oranges, j Cocoa Nut,\n\nFruits, shco ^ Lemons, i Citrons, &c.\n\nlittle but Cedar\n\nExcept that from the Sea ^$p£rma c -\n\nthey sometimes find thet wo j Amber Tease>»\nmost valuable Articles or C\n\nThe Island of Newfoundland, or rather the\n\nSeas adjacent, produce ar.j infinite Store of\nWhite Fish, which the English and French\nca ch upon the Banks or Sands, so call'd, over\nagainst the Island. They bring them on Sb-re\nto cure and prepare for Market, and so sell\nthem to other Merchants, who come in other\nShips to buy the Fish, and cany them away\ninto the Streights, to Spain and Italy, as also\nto Portugal. The French are allow’d by\nTreaty to make, that is, to cure their Fission\nsome Parts of the Back of the Islind: But the\nProperty and Sovereignty belongs to the Bri-\ntish Government.\n\nAlso they have, of late Years especially,\n\nset up a great Trade in the several harbours\nand Rivers of this Island of Newfourilland\nfor the Salmon Fishing: The Quantity they\nfind is very great, and the Fish large and\ngood. This occasions several Buildings, as\nwell of Dwelling-houses as Ware-houses and\nFish-houses, on the Banks of the Creeks and\nRivers where the Fisheries are erected; and\nthey have their several Bounds in these Ri-\nvers, made out by Stops and Wears, for the\nascertaining the Property of the Places re-\nspectively, as also for the more easy taking\nthe Fish.\n\nThese Buildings increasing as they do eve-\n\nry Year since the Peace, were not the Cold\nso excessively severe, and the Country itself so\nunhospitable and barren, that it discourages.\nthe People from Planting, would certainly\ncause Towns or Villages at least to be built\nin those Places, and would bring Numbers\nof People to fettle there, lather than to go\nback to England every Winter, and return\nevery Spring : which is, besides the Hazard\nof the Sea, exceeding chargeable and trouble-\nsome to the Fishermen themselves.\n\nBut it cannot be avoided, unless Numbers\n\nof People resolv’d to settle together, and to\nassist one another as a Company, as was the\nCafe in the fiist Planting the Colonies of\nNew-England, Virginia, and other Places;\nwhere, till a sufficient Quantity of Land was\ncured and planted, the People could not sub-\nsist themselves without constant Supplies from\nEurope, both of Men, Cattle and Provi-\nsions.\n\nThis Salmon Fishing at Newfoundland is\n\nchi:fly carried on by the Merchants of Cool,\nSouthampton, Weymouth, Lime, and other\nForts on the Western Parts of England, as is\nalso the White Fishing upon the Banks.\n\nN. B. Those who go to these Banks to fish,\n\nthat is, to take and cure, are call’d Fisher-\nBoats, and Newfoundland Ships, or in the\nSeamens Language, Newfoundland Men or\n'Jankers: But those Vessels sent by the\nMerchants to buy the Fish, and carry it eff\nto Spain, Italy, &c. as above, are distin-\ngpilh'd by Sack-men, and the Voyage is\ncall’d going for a Sack: And when a Ma-\nster of a Ship fays he is bound for New-\nfoundland, or for the Banks, his usual to\nask him, What, do yon go to fish,^ or go\nfor a Sack ? that is, to catch the Fish, or\nto buy. th\n\nh\n\nc\n\nm\n\no\n\nm\nb\n\nth\nfr\n\nAs to the other Islands .mention’d above,\n\ntheir Trade is all alike; ail their Product of\nwhatever Kind is exported to Great Britain\nonly, or to some or other of the British Co-\nlonies on the Continent of America. Nei-\nther is any Ship of any other Nation allow’d\nto enter, or unlade any thing there, nor any\nBritish Ship, but such as came last from\nGreat Britain, or from some particular Places\nlimited by the Act of Navigation, Distress of\nWeather, Hunger, Want of Water, or Pro- o\n\nft\nth\n\no\n\nto\nfh\n\na\n\na\n\nh\n\nv\nR\nI\nC\n\n‘\n\n‘\n\n‘\n\n*\n\n*\n\n‘\n\nS\n\no\nB\nI\n\nt\n\na\nR\nf\n\na\n\nr\n\nj\n\nsection from Pyrates and Enemies, only ex-\n\ncepte(L if any Ship comes to any Port in these\nIslands, and takes in a Loading to be deli-\nvers! in any other Country not subject to the\nGovernment of Great Britain, they are ob-\nliged first to touch at, and enter some Port,\nor Town, or Harbour of Great Britain, and\n\nthere to import the same at tie Custom-\nhouse, land the Goods, pay the Duty, or se-\ncure it as the Law directs ; and then they\nmay export the Goods again in the fame Ship\nor any other, drawing back by Certificate so\nmuch of the (aid Unties as the Law allows to\nbe return’d upon Exportation.\n\nThe Ej\n\nthey\nfrom :x eptior.s mentiond above are, that\n\nare allow’d to receive Salt and Wine\nthe Cape de Verde Islands, and ary\n\nother Parts; Wine from the Maderas, or\n\ncm the Canaries. Ar.d Engldh Ships in\ntheir Return sr >m India; or from America,\nor any cuher Pass of the World, may put in-\n\nany of these illfnds for Refreshment, but\n■ !1 r: c be p rmittfd to break Bulk, or put\n\nany of th ir Goods on Shore, except Gold\nand Silver in Specie.\n\n[To be continued.']\n\n"
    texts = regroup_texts(text_to_explode)

    for text in texts:
        text = clean_text(text)
        print(text)
        
        print("\n\n")