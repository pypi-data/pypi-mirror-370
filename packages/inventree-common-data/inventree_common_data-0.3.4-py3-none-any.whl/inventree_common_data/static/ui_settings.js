
export function renderPluginSettings(target, data) {
    let $is_superuser = data.user.isSuperuser() || data.user.isStaff() || false;
    let items = data.context || [];


    let overview_link = data.modelInformation?.partparametertemplate?.url_overview || '#';
    let data_text = Object.entries(items.latest_sources).map(([key, item]) => {
        return `<li>${item.name}: ${item.description} from <a href="${item?.source?.url}">${item?.source?.text}</a></li>`;
    }).join('');
    let username = data.user.username() || 'unknown';
    let superuser_text = $is_superuser ? 'Superuser' : 'not Superuser';

    target.innerHTML = `
    <i>InvenTree Common Data</i> is a provider for commonly used data. It provides various locked SelectionLists, that can be used in part and part category <a href="${overview_link}">parameters</a>.

    <h5>Available Sources:</h5>
    In their latest version
    <ul>
    ${data_text}
    </ul>

    User Info: <i>${username}</i> ${superuser_text}
    `;
}
