Feature: Pace to BPM Algorithm
  Calculate target running BPM limits given a pace and unit
  
  Scenario: Calculate BPM for 5:30 min/km pace with normal cadence
    Given a pace of "5:30" "min/km"
    And a cadence preference of "normal"
    When I calculate the target BPM
    Then the optimal BPM should be roughly 162
    And the lower bound should be 5 less than optimal
    And the upper bound should be 5 more than optimal

  Scenario: Calculate BPM for 8:00 min/mi pace with high cadence
    Given a pace of "8:00" "min/mi"
    And a cadence preference of "high"
    When I calculate the target BPM
    Then the optimal BPM should be roughly 171

  Scenario: Calculate BPM bounded by realistic ranges
    Given a pace of "3:00" "min/km"
    When I calculate the target BPM
    Then the optimal BPM should not exceed 190

  Scenario: Calculate BPM for slow walking pace
    Given a pace of "15:00" "min/km"
    When I calculate the target BPM
    Then the optimal BPM should not be less than 120
