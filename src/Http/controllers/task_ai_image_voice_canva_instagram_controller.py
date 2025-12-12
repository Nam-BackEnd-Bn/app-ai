"""Task controller."""

from pathlib import Path
from src.services.task_ai_image_voice_canva_instagram_service import TaskAIImageVoiceCanvaInstagramService


class TaskAIImageVoiceCanvaInstagramController:
    """Controller for handling task-related requests."""
    
    def __init__(self, service: TaskAIImageVoiceCanvaInstagramService, html_dir: Path):
        """
        Initialize controller with service.
        
        Args:
            service: TaskAIImageVoiceCanvaInstagramService instance
            html_dir: Path to HTML templates directory
        """
        self.service = service
        self.html_dir = html_dir
    
    def get_tasks(self, page: int = 1, per_page: int = 10) -> dict:
        """
        Get paginated list of tasks.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Dictionary with tasks and pagination info
        """
        try:
            result = self.service.get_all_tasks(page, per_page)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching tasks: {str(e)}',
                'data': None
            }
    
    def get_task(self, task_id: str) -> dict:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Dictionary with task data
        """
        try:
            task = self.task_service.get_task_by_id(task_id)
            if task:
                return {
                    'success': True,
                    'data': task
                }
            else:
                return {
                    'success': False,
                    'message': 'Task not found'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching task: {str(e)}'
            }
    
    def generate_table_html(self, page: int = 1, per_page: int = 10) -> str:
        """
        Generate table HTML with paginated task data.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            HTML string for the table page
        """
        # Get tasks from service
        result = self.get_tasks(page, per_page)
        
        if not result['success']:
            # Fallback to empty data if error
            tasks = []
            total = 0
            total_pages = 0
        else:
            data = result['data']
            tasks = data['tasks']
            total = data['total']
            total_pages = data['total_pages']
        
        # Helper function to safely escape HTML and format characters
        def safe_value(value):
            """Safely escape value for HTML display and prevent format() errors."""
            if value is None:
                return ''
            value_str = str(value)
            # Escape HTML special characters
            value_str = value_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Escape curly braces by doubling them to prevent format() errors
            value_str = value_str.replace('{', '{{').replace('}', '}}')
            return value_str
        
        # Generate table rows with all columns
        rows = ""
        for task in tasks:
            # Helper function to get status badge class
            def get_status_class(status):
                if not status:
                    return "status-pending"
                status_lower = status.lower()
                if "pending" in status_lower:
                    return "status-pending"
                elif "progress" in status_lower or "in progress" in status_lower:
                    return "status-progress"
                elif "completed" in status_lower or "complete" in status_lower:
                    return "status-completed"
                elif "failed" in status_lower or "error" in status_lower:
                    return "status-failed"
                return "status-pending"
            
            # Format dates
            created_at = task.get('createdAt', '')[:19] if task.get('createdAt') else ''
            updated_at = task.get('updatedAt', '')[:19] if task.get('updatedAt') else ''
            
            # Format URLs as links (escape the URL values)
            def format_url(url):
                if not url:
                    return ''
                # Escape HTML and format characters in URL
                escaped_url = safe_value(url)
                if len(url) > 30:
                    return f'<a href="{escaped_url}" class="url-link" target="_blank" title="{escaped_url}">{safe_value(url[:27])}...</a>'
                else:
                    return f'<a href="{escaped_url}" class="url-link" target="_blank">{escaped_url}</a>'
            
            status_img_class = get_status_class(task.get('statusImage', ''))
            status_voice_class = get_status_class(task.get('statusVoice', ''))
            status_canva_class = get_status_class(task.get('statusCanva', ''))
            
            # Escape all task values to prevent format() errors
            note_value = task.get('note', '')
            note_display = safe_value(note_value[:50] + '...' if note_value and len(note_value) > 50 else note_value)
            note_title = safe_value(note_value)
            
            rows += f"""
            <tr>
                <td>{safe_value(task.get('id', ''))}</td>
                <td>{safe_value(task.get('version', ''))}</td>
                <td>{safe_value(created_at)}</td>
                <td>{safe_value(updated_at)}</td>
                <td>{format_url(task.get('sheetUrl', ''))}</td>
                <td>{safe_value(task.get('sheetName', ''))}</td>
                <td>{safe_value(task.get('sheetID', ''))}</td>
                <td>{safe_value(task.get('rowID', ''))}</td>
                <td>{safe_value(task.get('row', ''))}</td>
                <td>{safe_value(task.get('accountSocial', ''))}</td>
                <td>{safe_value(task.get('typeRatioImage', ''))}</td>
                <td>{safe_value(task.get('accountAIImageInfo', ''))}</td>
                <td>{safe_value(task.get('accountEmailImage', ''))}</td>
                <td>{safe_value(task.get('accountAIImage', ''))}</td>
                <td>{safe_value(task.get('channelImage', ''))}</td>
                <td>{safe_value(task.get('promptThumbInput', ''))}</td>
                <td>{format_url(task.get('thumbOutputUrl', ''))}</td>
                <td>{safe_value(task.get('promptPage1Input', ''))}</td>
                <td>{format_url(task.get('page1OutputUrl', ''))}</td>
                <td>{safe_value(task.get('promptPage2Input', ''))}</td>
                <td>{format_url(task.get('page2OutputUrl', ''))}</td>
                <td>{safe_value(task.get('promptNichePage3Input', ''))}</td>
                <td>{format_url(task.get('nichePage3OutputUrl', ''))}</td>
                <td>{safe_value(task.get('promptNichePage4Input', ''))}</td>
                <td>{format_url(task.get('nichePage4OutputUrl', ''))}</td>
                <td>{safe_value(task.get('promptNichePage5Input', ''))}</td>
                <td>{format_url(task.get('nichePage5OutputUrl', ''))}</td>
                <td>{safe_value(task.get('channelVoice', ''))}</td>
                <td>{safe_value(task.get('accountAIVoice', ''))}</td>
                <td>{safe_value(task.get('accountAIVoiceInfo', ''))}</td>
                <td>{safe_value(task.get('accountEmailVoice', ''))}</td>
                <td>{safe_value(task.get('promptVoicePage1Input', ''))}</td>
                <td>{format_url(task.get('voicePage1OutputUrl', ''))}</td>
                <td>{safe_value(task.get('promptVoicePage3456Input', ''))}</td>
                <td>{format_url(task.get('voicePage3456OutputUrl', ''))}</td>
                <td>{safe_value(task.get('billetCharacterVoiceSpeaker1', ''))}</td>
                <td>{safe_value(task.get('billetCharacterVoiceSpeaker2', ''))}</td>
                <td>{safe_value(task.get('typePost', ''))}</td>
                <td>{safe_value(task.get('titlePool', ''))}</td>
                <td>{safe_value(task.get('pool1', ''))}</td>
                <td>{safe_value(task.get('pool2', ''))}</td>
                <td>{safe_value(task.get('pool3', ''))}</td>
                <td>{safe_value(task.get('textFirstPage2', ''))}</td>
                <td>{safe_value(task.get('textSecondPage2', ''))}</td>
                <td>{safe_value(task.get('textPage6', ''))}</td>
                <td>{format_url(task.get('linkAddHistory', ''))}</td>
                <td>{safe_value(task.get('nicheLinkCategory', ''))}</td>
                <td>{safe_value(task.get('styleName', ''))}</td>
                <td>{safe_value(task.get('backgroundForPage3', ''))}</td>
                <td>{safe_value(task.get('backgroundForPage4', ''))}</td>
                <td>{safe_value(task.get('backgroundForPage5', ''))}</td>
                <td>{safe_value(task.get('backgroundForPage6', ''))}</td>
                <td>{safe_value(task.get('effectAudioThumbnail', ''))}</td>
                <td>{safe_value(task.get('effectAudioPage345', ''))}</td>
                <td>{safe_value(task.get('bgRemoveBackground345', ''))}</td>
                <td>{safe_value(task.get('fontText1', ''))}</td>
                <td>{safe_value(task.get('fontText2', ''))}</td>
                <td>{format_url(task.get('linkCanvaScript', ''))}</td>
                <td>{format_url(task.get('linkCanvaVideo', ''))}</td>
                <td>{format_url(task.get('linkCanvaImageThumb', ''))}</td>
                <td>{format_url(task.get('linkCanvaImage1', ''))}</td>
                <td>{format_url(task.get('linkCanvaImage2', ''))}</td>
                <td>{format_url(task.get('linkCanvaImage3', ''))}</td>
                <td>{format_url(task.get('linkCanvaImage4', ''))}</td>
                <td>{format_url(task.get('linkCanvaImage5', ''))}</td>
                <td title="{note_title}">{note_display}</td>
                <td><span class="status-badge {status_img_class}">{safe_value(task.get('statusImage', '') or 'N/A')}</span></td>
                <td><span class="status-badge {status_voice_class}">{safe_value(task.get('statusVoice', '') or 'N/A')}</span></td>
                <td><span class="status-badge {status_canva_class}">{safe_value(task.get('statusCanva', '') or 'N/A')}</span></td>
                <td>{safe_value(task.get('createdBy', ''))}</td>
                <td>{safe_value(task.get('updatedBy', ''))}</td>
            </tr>
            """
        
        # Generate pagination
        pagination = ""
        if total_pages > 0:
            for i in range(1, total_pages + 1):
                active = "active" if i == page else ""
                pagination += f'<button class="page-btn {active}" onclick="changePage({i})">{i}</button>'
        
        # Generate page select dropdown options
        page_select = ""
        if total_pages > 0:
            for i in range(1, total_pages + 1):
                selected = "selected" if i == page else ""
                page_select += f'<option value="{i}" {selected}>Page {i}</option>'
        else:
            page_select = '<option value="1">Page 1</option>'
        
        # Load template and replace placeholders using string replacement (safer than format())
        template_file = self.html_dir / "task_table_template.html"
        with open(template_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Use string replacement instead of format() to avoid issues with braces in data
        html = html.replace('{rows}', rows)
        html = html.replace('{pagination}', pagination)
        html = html.replace('{pageSelect}', page_select)
        
        return html

