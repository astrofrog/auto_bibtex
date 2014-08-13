TEX = """
text here \citet{robitaille:08:2413}
more \cite{forbrich:10:1453} text
(\citealt{robitaille:06:256})
"""

EXPECTED = r"""
@ARTICLE{forbrich:10:1453,
   author = {{Forbrich}, J. and {Tappe}, A. and {Robitaille}, T. and {Muench}, A.~A. and 
	{Teixeira}, P.~S. and {Lada}, E.~A. and {Stolte}, A. and {Lada}, C.~J.
	},
    title = "{Disentangling Protostellar Evolutionary Stages in Clustered Environments Using Spitzer-IRS Spectra and Comprehensive Spectral Energy Distribution Modeling}",
  journal = {\apj},
archivePrefix = "arXiv",
 primaryClass = "astro-ph.SR",
 keywords = {circumstellar matter, infrared: stars, open clusters and associations: individual: NGC 2264 IC 348},
     year = 2010,
    month = jun,
   volume = 716,
    pages = {1453-1477},
      doi = {10.1088/0004-637X/716/2/1453},
   adsurl = {http://adsabs.harvard.edu/abs/2010ApJ...716.1453F},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@ARTICLE{robitaille:06:256,
   author = {{Robitaille}, T.~P. and {Whitney}, B.~A. and {Indebetouw}, R. and 
	{Wood}, K. and {Denzmore}, P.},
    title = "{Interpreting Spectral Energy Distributions from Young Stellar Objects. I. A Grid of 200,000 YSO Model SEDs}",
  journal = {\apjs},
 keywords = {Astronomical Data Bases: Miscellaneous, Stars: Circumstellar Matter, Infrared: Stars, Polarization, Radiative Transfer, Stars: Formation, Stars: Pre-Main-Sequence},
     year = 2006,
    month = dec,
   volume = 167,
    pages = {256-285},
      doi = {10.1086/508424},
   adsurl = {http://adsabs.harvard.edu/abs/2006ApJS..167..256R},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@ARTICLE{robitaille:08:2413,
   author = {{Robitaille}, T.~P. and {Meade}, M.~R. and {Babler}, B.~L. and 
	{Whitney}, B.~A. and {Johnston}, K.~G. and {Indebetouw}, R. and 
	{Cohen}, M. and {Povich}, M.~S. and {Sewilo}, M. and {Benjamin}, R.~A. and 
	{Churchwell}, E.},
    title = "{Intrinsically Red Sources Observed by Spitzer in the Galactic Midplane}",
  journal = {\aj},
archivePrefix = "arXiv",
 keywords = {catalogs, infrared: stars, Galaxy: stellar content, planetary nebulae: general, stars: AGB and post-AGB, stars: formation},
     year = 2008,
    month = dec,
   volume = 136,
    pages = {2413-2440},
      doi = {10.1088/0004-6256/136/6/2413},
   adsurl = {http://adsabs.harvard.edu/abs/2008AJ....136.2413R},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
"""

from auto_bibtex import main

def test_main(tmpdir):
    filename = tmpdir.join('ms.tex').strpath
    with open(filename, 'w') as f:
        f.write(TEX)
    output = main(filename)
    assert output.strip() == EXPECTED.strip()