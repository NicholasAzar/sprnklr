import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { GoogleTargetAccount, TargetAccount, TargetsService } from '../targets.service';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import { remote } from 'electron';

@Component({
  selector: 'add-target',
  templateUrl: './add-target.component.html',
})
export class AddTargetComponent {

  targetTypeFormGroup: FormGroup;
  pathDetailsFormGroup: FormGroup;
  googleDetailsFormGroup: FormGroup;
  private googleTargetAccount:TargetAccount<GoogleTargetAccount>;

  constructor(public dialogRef: MatDialogRef<AddTargetComponent>,
    @Inject(MAT_DIALOG_DATA) public data: AddTargetData,
    private formBuilder: FormBuilder,
    private targetsService: TargetsService) {}

  ngOnInit() {
    this.targetTypeFormGroup = this.formBuilder.group({
      targetTypeCtrl : ['', Validators.required]
    });
    this.pathDetailsFormGroup = this.formBuilder.group({
      pathCtrl: ['', Validators.required]
    })
    this.googleDetailsFormGroup = this.formBuilder.group({
      emailCtrl: ['', Validators.required],
      accessTokenCtrl: ['', Validators.required],
      refreshTokenCtrl: ['', Validators.required]
    });

    console.log("pathDetailsFormGroup", this.pathDetailsFormGroup);
  }

  get targetType() {
    return this.targetTypeFormGroup.controls?.targetTypeCtrl?.value;
  }

  selectPath() {
    const result = remote.dialog.showOpenDialogSync(null, {properties: ['openDirectory']});
    console.log('result: ', result);
    if (result && result.length > 0) {
      this.pathDetailsFormGroup.controls.pathCtrl.setValue(result[0]);
    } else {
      console.log("You didn't select a folder");
    }
  }

  async getGoogleAccount() {
    // Trigger add account
    await this.targetsService.getGoogleAccount().then((targetAccount:TargetAccount<GoogleTargetAccount>) => {
      this.googleTargetAccount = targetAccount;
      // apply to form
      this.googleDetailsFormGroup.controls.emailCtrl.setValue(targetAccount.account.email);
      this.googleDetailsFormGroup.controls.accessTokenCtrl.setValue(targetAccount.account.accessToken);
      this.googleDetailsFormGroup.controls.refreshTokenCtrl.setValue(targetAccount.account.refreshToken);
    });
  }

  applyChanges() {
    if (this.targetType === 'path') {
      this.targetsService.persistPath(this.pathDetailsFormGroup.controls.pathCtrl.value);
    } else if (this.targetType === 'google') {
      this.targetsService.persistGoogleAccount(this.googleTargetAccount);
    }
    this.dialogRef.close();
  }

  resetForms() {
    
  }
}

export interface AddTargetData {
  account:TargetAccount
}
