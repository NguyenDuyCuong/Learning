import { ChangeDetectionStrategy, Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { UserAction } from '../../coffee-list.constants';
import { Candidate } from '../../types/candidate';

@Component({
  selector: 'app-coffee-candidate',
  templateUrl: './coffee-candidate.component.html',
  styleUrls: ['./coffee-candidate.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CoffeeCandidateComponent {
  @Input()
  candidate: Candidate;
  @Output()
  onUserAction = new EventEmitter<UserAction>();

  UserAction = UserAction;
}
