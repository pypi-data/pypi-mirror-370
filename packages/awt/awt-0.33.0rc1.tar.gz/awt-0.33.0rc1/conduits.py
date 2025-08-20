from abiflib import (
    convert_abif_to_jabmod,
    htmltable_pairwise_and_winlosstie,
    get_Copeland_winners,
    html_score_and_star,
    ABIFVotelineException,
    full_copecount_from_abifmodel,
    copecount_diagram,
    IRV_dict_from_jabmod,
    get_IRV_report,
    FPTP_result_from_abifmodel,
    get_FPTP_report,
    pairwise_count_dict,
    STAR_result_from_abifmodel,
    scaled_scores
)
from abiflib.irv_tally import IRV_result_from_abifmodel
from abiflib.pairwise_tally import pairwise_result_from_abifmodel
from abiflib.approval_tally import (
    approval_result_from_abifmodel,
    get_approval_report
)
from html_util import generate_candidate_colors

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ResultConduit:
    jabmod: Dict[str, Any] = field(default_factory=dict)
    resblob: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.jabmod:
            raise TypeError(
                "Please pass in jabmod= param on ResultsConduit init")
        self.resblob = {}

    def _extract_notices(self, method_tag: str, result_dict: dict) -> None:
        """Extract notices from voting method result using consistent tag-based naming"""
        if 'notices' not in self.resblob:
            self.resblob['notices'] = {}
        self.resblob['notices'][method_tag] = result_dict.get('notices', [])

    def update_FPTP_result(self, jabmod) -> "ResultConduit":
        """Add FPTP result to resblob"""
        fptp_result = FPTP_result_from_abifmodel(jabmod)
        self.resblob['FPTP_result'] = fptp_result
        self._extract_notices('fptp', fptp_result)
        # self.resblob['FPTP_text'] = get_FPTP_report(jabmod)
        return self

    def update_IRV_result(self, jabmod, include_irv_extra=False) -> "ResultConduit":
        """Add IRV result to resblob"""

        # Backwards compatibility with abiflib v0.32.0
        try:
            # TODO: rename to "IRV_result"
            self.resblob['IRV_dict'] = IRV_dict_from_jabmod(
                jabmod, include_irv_extra=include_irv_extra)
        except TypeError as e:
            import datetime
            print(f" ------------ [{datetime.datetime.now():%d/%b/%Y %H:%M:%S}] "
                  f"Upgrade abiflib to v0.32.1 or later for IRVextra support.")
            self.resblob['IRV_dict'] = IRV_dict_from_jabmod(jabmod)

        # Create the IRV result with summary data
        self.resblob['IRV_result'] = IRV_result_from_abifmodel(jabmod)

        # Convert sets to lists for JSON serialization in templates
        irv_dict = self.resblob['IRV_dict']
        if 'roundmeta' in irv_dict:
            for round_meta in irv_dict['roundmeta']:
                if 'hypothetical_transfers' in round_meta:
                    round_meta['next_choices'] = round_meta.pop(
                        'hypothetical_transfers')
                for key in ['eliminated', 'all_eliminated', 'bottomtie']:
                    if key in round_meta and isinstance(round_meta[key], set):
                        round_meta[key] = list(round_meta[key])

        self.resblob['IRV_text'] = get_IRV_report(self.resblob['IRV_dict'])
        self._extract_notices('irv', self.resblob['IRV_dict'])
        return self

    def update_pairwise_result(self, jabmod) -> "ResultConduit":
        # Get pairwise result with notices first
        pairwise_result = pairwise_result_from_abifmodel(jabmod)
        pairwise_matrix = pairwise_result['pairwise_matrix']

        # Use the same pairwise matrix for copecount to ensure consistency
        copecount = full_copecount_from_abifmodel(jabmod, pairdict=pairwise_matrix)
        copewinners = get_Copeland_winners(copecount)
        cwstring = ", ".join(copewinners)
        self.resblob['copewinners'] = copewinners
        self.resblob['copewinnerstring'] = cwstring
        self.resblob['is_copeland_tie'] = len(copewinners) > 1
        self.resblob['dotsvg_html'] = copecount_diagram(
            copecount, outformat='svg')
        self.resblob['pairwise_dict'] = pairwise_matrix
        # Extract notices using consistent method (following STAR/approval pattern)
        self._extract_notices('pairwise', pairwise_result)
        self.resblob['pairwise_html'] = htmltable_pairwise_and_winlosstie(jabmod,
                                                                          snippet=True,
                                                                          validate=True,
                                                                          modlimit=2500)
        if jabmod and 'candidates' in jabmod:
            self.resblob['colordict'] = generate_candidate_colors(
                jabmod['candidates'].keys())
        else:
            self.resblob['colordict'] = {}
        return self

    def update_STAR_result(self, jabmod, colordict=None) -> "ResultConduit":
        scorestar = {}
        self.resblob['STAR_html'] = html_score_and_star(jabmod)
        scoremodel = STAR_result_from_abifmodel(jabmod)
        scorestar['scoremodel'] = scoremodel
        stardict = scaled_scores(jabmod, target_scale=50)
        from awt import add_html_hints_to_stardict
        scorestar['starscale'] = \
            add_html_hints_to_stardict(
                scorestar['scoremodel'], stardict, colordict)
        # Extract notices using consistent method
        self._extract_notices('star', scoremodel)

        # Keep backward compatibility for now
        star_notices = scoremodel.get('notices', [])
        if star_notices:
            scorestar['star_foot'] = \
                'NOTE: Since ratings or stars are not present in the provided ballots, ' + \
                'allocated stars are estimated using a Borda-like formula.'

        self.resblob['scorestardict'] = scorestar
        return self

    def update_approval_result(self, jabmod) -> "ResultConduit":
        """Add approval voting result to resblob"""
        approval_result = approval_result_from_abifmodel(jabmod)
        self.resblob['approval_result'] = approval_result
        self.resblob['approval_text'] = get_approval_report(jabmod)
        # Extract notices using consistent method
        self._extract_notices('approval', approval_result)
        # Keep backward compatibility
        self.resblob['approval_notices'] = approval_result.get('notices', [])
        return self

    def update_all(self, jabmod):
        '''Call all of the update methods for updating resconduit blob'''
        # This is example code to replace the old _get_jabmod_to_resblob
        resconduit = ResultConduit(jabmod=jabmod)
        resconduit = resconduit.update_FPTP_result(jabmod)
        resconduit = resconduit.update_IRV_result(jabmod)
        resconduit = resconduit.update_pairwise_result(jabmod)
        resconduit = resconduit.update_STAR_result(jabmod)
        resconduit = resconduit.update_approval_result(jabmod)
        return self
