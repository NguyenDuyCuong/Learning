import {ICandidate} from './candidate';
import {Sort} from '@shared/types/sort';

export interface CandidateList {
    candidates: ICandidate[];
    sort: Sort;
}
