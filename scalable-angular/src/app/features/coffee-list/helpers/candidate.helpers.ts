import {Candidate} from '../types/candidate';
import {UserAction} from '../coffee-list.constants';
import {User} from '@core/user/types/user';
import * as dateHelpers from '@shared/helpers/date.helpers';

export function getCandidatesInStoreFormat(
    candidates: Candidate[],
    user: User
): Candidate[] {
    return candidates.map(candidate => {
        candidate = prettifyVoteDates(candidate);
        candidate = getCandidateWithUserActions(candidate, user);
        return candidate;
    });
}

function prettifyVoteDates(candidate: Candidate): Candidate {
    return {
        ...candidate,
        votes: candidate.votes.map(vote => {
            return {
                user: vote.user,
                date: dateHelpers.convertISOToHuman(vote.date),
            };
        }),
    } as Candidate;
}

function getCandidateWithUserActions(
    candidate: Candidate,
    user: User
): Candidate {
    return {
        ...candidate,
        userAction: hasUserVotedForCandidate(user, candidate)
            ? UserAction.RemoveVote
            : UserAction.AddVote,
    } as Candidate;
}

function hasUserVotedForCandidate(user: User, candidate: Candidate) {
    for (let vote of candidate.votes) {
        if (vote.user === user.email) {
            return true;
        }
    }
    return false;
}
