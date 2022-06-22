import {Vote} from './vote';
import {RequestState} from '@shared/types/request-state';
import {UserAction} from '../coffee-list.constants';

export interface ICandidate {
    id: number;
    name: string;
    votes: Vote[];
    userAction?: UserAction;
    updateRequest?: RequestState;

    isNull(): boolean;
}

export class Candidate implements ICandidate {
    id: number;
    name: string;
    votes: Vote[];
    userAction?: UserAction;
    updateRequest?: RequestState;

    isNull(): boolean { return false; }
}
