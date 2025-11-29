// script.js (минимум для демо)
document.getElementById('btn-start').onclick = () => showScreen('auth');
document.getElementById('auth-form').onsubmit = e => { e.preventDefault(); showScreen('quests'); };
document.getElementById('btn-back-quests').onclick = () => showScreen('quests');
document.getElementById('btn-skip-lead').onclick = () => showScreen('quests');
document.getElementById('lead-form').onsubmit = e => { e.preventDefault(); showScreen('quests'); };
document.getElementById('btn-next-quest').onclick = () => showScreen('quests');
document.getElementById('btn-go-shop').onclick = () => showScreen('shop');

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.onclick = () => showScreen(btn.dataset.screen);
});

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
  document.getElementById(`screen-${id}`).classList.add('active');
  
  // выделение активной вкладки
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelector(`.nav-item[data-screen="${id}"]`)?.classList.add('active');
}