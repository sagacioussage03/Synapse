// frontend/src/features/bots/BotsPage.jsx
import AlarmBotCard from './AlarmBotCard';

export default function BotsPage() {
  return (
    <div className="app-main">
      <AlarmBotCard />
      {/* Later: <SomeOtherBotCard /> */}
    </div>
  );
}