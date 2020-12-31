import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { TargetAccount, TargetsService } from './targets.service';

@Component({
  selector: 'targets',
  templateUrl: './targets.component.html',
  styleUrls: ['./targets.component.scss']
})
export class TargetsComponent {

  targetAccounts:Observable<TargetAccount[]>;

  constructor(private targetService:TargetsService) {
    this.targetAccounts = this.targetService.targets;
  }

  addAccount() {
    console.log("IMPLEMENT ME");
  }
}

