import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html',
  styleUrl: './portfolio.component.css'
})
export class PortfolioComponent {
  @Output() portfolioChanged = new EventEmitter<string>();

  portfolios: string[] = ['Portfolio 1', 'Portfolio 2', 'Portfolio 3'];
  selectedPortfolio: string = this.portfolios[0];

  onPortfolioChange(event: any) {
    this.portfolioChanged.emit(this.selectedPortfolio);
  }
}
