import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NetworkMapComponent } from './network-map.component';

describe('NetworkMapComponent', () => {
  let component: NetworkMapComponent;
  let fixture: ComponentFixture<NetworkMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NetworkMapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(NetworkMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
