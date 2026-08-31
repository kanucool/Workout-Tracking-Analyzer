import { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';

export default function WorkoutAnalytics({ workoutData } ) {
    const [currentExercise, setCurrentExercise] = useState('');
    
    // Brzycki's Formula
    const oneRepMax = (weight, reps) => {
        // The formula is inaccurate for high reps
        // Use a different estimation if > 10
        if (reps > 10) return weight * reps / 10;
        return weight * (36 / (37 - reps));
    }

    const uniqueExercises = useMemo(() => {
        const exercises = [];
        for (let workout of workoutData) {
            for (let exercise of workout.exercises) {
                exercises.push(exercise.name);
            }
        }
        return [...new Set(exercises)].sort();
    }, [workoutData]);

    const chartData = useMemo(() => {
        if (!currentExercise) return [];

        const oneRepMaxSums = {};
        workoutData.forEach(workout => {
            let date = workout.date;
            for (let exercise of workout.exercises.filter(
                exercise => exercise.name == currentExercise
            )) {
                for (let set of exercise.sets) {
                    oneRepMaxSums[date] = oneRepMaxSums[date] || {"sum": 0.0, "count": 0};
                    oneRepMaxSums[date]["sum"] += oneRepMax(set.weight, set.reps);
                    oneRepMaxSums[date]["count"]++;
                }
            }
        });

        const oneRepMaxes = Object.entries(oneRepMaxSums).map(entry => {
            let date = entry[0];
            let obj = entry[1];
            return {"date": date, "oneRepMax": obj["sum"] / obj["count"]};
        });

        return oneRepMaxes.sort((a, b) => a["date"].localeCompare(b["date"]));
    }, [currentExercise, workoutData]);

    console.log(uniqueExercises);

    return (
    <div>
    <LineChart style={{ width: '100%', aspectRatio: 1.618, maxWidth: 600 }} responsive data={chartData}>
      <CartesianGrid />
      <Line dataKey="oneRepMax" />
      <XAxis dataKey="date" />
      <YAxis /> 
    </LineChart>
    <select name="exercises" onChange={(e) => {setCurrentExercise(e.target.value)}}>
        {uniqueExercises.map(exercise => {
            return <option value={exercise}>{exercise}</option>
        })}
    </select>
    </div>
     );
}