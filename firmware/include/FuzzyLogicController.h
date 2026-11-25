#ifndef FUZZY_LOGIC_CONTROLLER_H
#define FUZZY_LOGIC_CONTROLLER_H

#include <math.h>

/**
 * Fuzzy Logic Controller (FLC)
 * Implements Triangular Membership Functions and Centroid Defuzzification
 * for Obstacle Distance to Motor Speed regulation.
 */

struct FuzzyMembership {
    float muNear;
    float muMedium;
    float muFar;
};

struct FLCResult {
    float distanceCm;
    FuzzyMembership membership;
    float speedPercent;
    int pwmValue;
    bool isStopped;
};

class FuzzyLogicController {
public:
    // Distance Membership Parameters
    static constexpr float NEAR_PEAK = 0.0f;
    static constexpr float NEAR_RIGHT = 60.0f;

    static constexpr float MED_LEFT = 40.0f;
    static constexpr float MED_PEAK = 100.0f;
    static constexpr float MED_RIGHT = 160.0f;

    static constexpr float FAR_LEFT = 140.0f;
    static constexpr float FAR_PEAK = 200.0f;

    // Speed Consequents
    static constexpr float SPEED_SLOW   = 20.0f;  // 20%
    static constexpr float SPEED_MEDIUM = 60.0f;  // 60%
    static constexpr float SPEED_FAST   = 100.0f; // 100%

    static constexpr float STOP_DISTANCE_CM = 20.0f;
    static constexpr float MAX_DISTANCE_CM  = 200.0f;

    static float trimf(float x, float a, float b, float c) {
        if (x <= a || x >= c) return 0.0f;
        if (x == b) return 1.0f;
        if (x > a && x < b) return (x - a) / (b - a);
        return (c - x) / (c - b);
    }

    static float trimfLeft(float x, float b, float c) {
        if (x <= b) return 1.0f;
        if (x >= c) return 0.0f;
        return (c - x) / (c - b);
    }

    static float trimfRight(float x, float a, float b) {
        if (x <= a) return 0.0f;
        if (x >= b) return 1.0f;
        return (x - a) / (b - a);
    }

    static FuzzyMembership fuzzify(float distanceCm) {
        float d = distanceCm;
        if (d < 0.0f) d = 0.0f;
        if (d > MAX_DISTANCE_CM) d = MAX_DISTANCE_CM;

        FuzzyMembership mem;
        mem.muNear   = trimfLeft(d, NEAR_PEAK, NEAR_RIGHT);
        mem.muMedium = trimf(d, MED_LEFT, MED_PEAK, MED_RIGHT);
        mem.muFar    = trimfRight(d, FAR_LEFT, FAR_PEAK);
        return mem;
    }

    static FLCResult compute(float distanceCm) {
        FLCResult result;
        float d = distanceCm;
        if (d < 0.0f) d = 0.0f;
        if (d > MAX_DISTANCE_CM) d = MAX_DISTANCE_CM;
        result.distanceCm = d;

        result.membership = fuzzify(d);

        if (distanceCm <= STOP_DISTANCE_CM) {
            result.isStopped = true;
            result.speedPercent = 0.0f;
            result.pwmValue = 0;
            return result;
        }

        result.isStopped = false;

        float num = (result.membership.muNear * SPEED_SLOW) +
                    (result.membership.muMedium * SPEED_MEDIUM) +
                    (result.membership.muFar * SPEED_FAST);
        float den = result.membership.muNear +
                    result.membership.muMedium +
                    result.membership.muFar;

        float speed = (den > 0.0001f) ? (num / den) : 0.0f;
        if (speed < 0.0f) speed = 0.0f;
        if (speed > 100.0f) speed = 100.0f;

        result.speedPercent = speed;
        result.pwmValue = (int)roundf((speed / 100.0f) * 255.0f);
        if (result.pwmValue > 255) result.pwmValue = 255;
        if (result.pwmValue < 0) result.pwmValue = 0;

        return result;
    }
};

#endif // FUZZY_LOGIC_CONTROLLER_H
