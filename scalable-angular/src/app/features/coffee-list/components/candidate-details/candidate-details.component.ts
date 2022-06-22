import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Candidate } from '../../types/candidate';
import { NullCandidate } from '../../types/null-candidate';

@Component({
  selector: 'app-candidate-details',
  templateUrl: './candidate-details.component.html',
  styleUrls: ['./candidate-details.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CandidateDetailsComponent {
  @Input()
  candidate?: Candidate = new NullCandidate();
}
