Feature: Playlist Assembly Logic
  Assemble a playlist with enough tracks to cover the run duration

  Scenario: Calculate total duration for a 5km run at 6:00 pace
    Given a distance of 5.0 "km"
    And a pace of "6:00"
    When I calculate the duration
    Then the raw duration should be 1800 seconds

  Scenario: Assemble tracks to fill a 10 minute requirement
    Given a target duration of 600 seconds
    And a pool of tracks each 200 seconds long
    When I assemble the playlist
    Then I should have 3 tracks in the playlist
    Then the playlist duration should be 600 seconds
