import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { SourceAccount, SourcesService } from './sources.service';

@Component({
  selector: 'sources',
  templateUrl: './sources.component.html',
  styleUrls: ['./sources.component.scss']
})
export class SourcesComponent {

  sourceAccounts:Observable<SourceAccount[]>;

  constructor(private sourcesService:SourcesService) {
    this.sourceAccounts = this.sourcesService.sources;
  }

  addAccount() {
    // TODO(nzar): Showing waiting dialog
    this.sourcesService.addAccount();
  }

  clearAllSources() {
    this.sourcesService.clearAllSources();
  }
}

