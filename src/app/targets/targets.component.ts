import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { TargetAccount, TargetsService } from './targets.service';
import { AddTargetComponent } from './add-target/add-target.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'targets',
  templateUrl: './targets.component.html',
  styleUrls: ['./targets.component.scss']
})
export class TargetsComponent {

  targetAccounts:Observable<TargetAccount[]>;

  constructor(private targetService:TargetsService, private dialog: MatDialog) {
    this.targetAccounts = this.targetService.targets;
  }

  openAddAccountDialog() {
    const dialogRef = this.dialog.open(AddTargetComponent, {
      width: '500px',
      data: {}
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed: ', result);
    });
  }
}

